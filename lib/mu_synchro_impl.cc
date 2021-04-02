/* -*- c++ -*- */
/*
 * Copyright 2020 Joachim Tapparel TCL@EPFL.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "mu_synchro_impl.h"

namespace gr {
  namespace lora_sdr {

    mu_synchro::sptr
    mu_synchro::make(uint8_t sf, uint8_t os_factor, uint32_t len)
    {
      return gnuradio::get_initial_sptr
        (new mu_synchro_impl(sf, os_factor, len));
    }

    /*
     * The private constructor
     */
    mu_synchro_impl::mu_synchro_impl(uint8_t sf, uint8_t os_factor, uint32_t len)
      : gr::block("mu_synchro",
      gr::io_signature::make(1, 1, sizeof(gr_complex)),
      gr::io_signature::make2(1, 2, sizeof(gr_complex),sizeof(uint32_t)))
    {
            m_sf = sf;
            m_os_factor = os_factor;
            m_len = len;

            m_n_up = 8;
            m_N = (uint32_t)(1u << m_sf);
            m_samples_per_symbol = m_N*m_os_factor;
            m_sync_state = IDLE;
            m_power1 = 0;
            m_power2 = 0;

            two_users = false;
    }

    /*
    * Our virtual destructor.
    */
    mu_synchro_impl::~mu_synchro_impl()
    {}

    void mu_synchro_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        //ninput_items_required[0] = std::max(m_samples_per_symbol, noutput_items * m_os_factor);
        ninput_items_required[0] = m_samples_per_symbol;
    }

    void mu_synchro_impl::add_tag(double power1, double power2, long win_len,
                                  Symbol_type Tu, Symbol_type Ti1, Symbol_type Ti2,
                                  double tau, double delta_cfo, int offset){
        pmt::pmt_t window_tag = pmt::make_dict();

        window_tag = pmt::dict_add(window_tag,pmt::intern("power1"), pmt::from_double(power1));
        window_tag = pmt::dict_add(window_tag,pmt::intern("power2"), pmt::from_double(power2));
        window_tag = pmt::dict_add(window_tag,pmt::intern("win_len"), pmt::from_long(win_len));
        window_tag = pmt::dict_add(window_tag,pmt::intern("Tu"), pmt::from_long(Tu));
        window_tag = pmt::dict_add(window_tag,pmt::intern("Ti1"), pmt::from_long(Ti1));
        window_tag = pmt::dict_add(window_tag,pmt::intern("Ti2"), pmt::from_long(Ti2));
        window_tag = pmt::dict_add(window_tag,pmt::intern("tau"),pmt::from_double(tau));
        window_tag = pmt::dict_add(window_tag,pmt::intern("delta_cfo"),pmt::from_double(delta_cfo));
        if(win_len > 0) // the algorithm might want to add windows of length 0, just ignore them
            add_item_tag(0, nitems_written(0)+offset, pmt::string_to_symbol("new_window"), window_tag);

        #ifdef GRLORA_DEBUG
        std::cout <<"[mu_synchro_impl.cc] "<< "\toffset "<< nitems_written(0) <<", power1 "<<power1<< ", power2 "<<
        power2<<", T_u= "<<Tu<<", T_i= "<<Ti1<<" "<<Ti2 <<", win_len= "<<win_len<<", tau= "<<tau<<", delta_cfo "<<delta_cfo<< std::endl;
        #endif
    }

    Symbol_type mu_synchro_impl::get_type(int cnt) {
        Symbol_type type;
        if (cnt<0)
            type = VOID;
        else if(cnt < m_n_up * m_N )
            type = UPCHIRP;
        else if(cnt < (m_n_up + 2)* m_N)
            type = SYNC_WORD;
        else if(cnt < (m_n_up + 4)* m_N)
            type = DOWNCHIRP;
        else if(cnt < (m_n_up + 4.25)* m_N)
            type = QUARTER_DOWN;
        else if(cnt < (m_n_up + 4.25 + m_len)* m_N)
            type = PAYLOAD;
        else if (cnt >= (m_n_up + 4.25 + m_len)* m_N)
            type = VOID;
        else //should never get there
            type = UNDETERMINED;

        return type;
    }



     std::tuple<int,int,int> mu_synchro_impl::sync_frame( const gr_complex *in, gr_complex *out, uint32_t *state_out , int offset, int state_offset)
    {
        int nitems_to_output = 0;
        int nstate_to_output = 0;

        std::vector<tag_t> tags;
        get_tags_in_window(tags,0,0,m_samples_per_symbol,pmt::string_to_symbol("new_user"));

        int win_len;
        bool realign_to_new = false; //used to debug
        int new_poly = 0;
        double delta_cfo = 0;        

        Symbol_type type;

        pmt::pmt_t err = pmt::string_to_symbol("error");
        user new_user;
        for (size_t i = 0; i < tags.size(); i++) {
            new_user.sto_int = pmt::to_long (pmt::dict_ref(tags[i].value,pmt::string_to_symbol("sto_int"),err));
            new_user.sto_frac = pmt::to_double(pmt::dict_ref(tags[i].value,pmt::string_to_symbol("sto_frac"),err));
            new_user.cfo_int = pmt::to_long (pmt::dict_ref(tags[i].value,pmt::string_to_symbol("cfo_int"),err));
            new_user.cfo_frac = pmt::to_double(pmt::dict_ref(tags[i].value,pmt::string_to_symbol("cfo_frac"),err));
            new_user.power = pmt::to_double(pmt::dict_ref(tags[i].value,pmt::string_to_symbol("power"),err));
            #ifdef GRLORA_DEBUG
            std::cout <<"[mu_synchro_impl.cc] "<< "new user: "<<std::to_string(new_user.power)<<", "<<std::to_string(new_user.cfo_int)<<", "<<std::to_string(new_user.sto_int)<<", "<<std::to_string(new_user.sto_frac)<<", "<<std::to_string(new_user.cfo_frac)<<", "<< std::endl;
            #endif
        }
        switch (m_sync_state) {
            case IDLE:
                if(tags.size() == 1) {
                    tag_t tag = tags[0];
                    if(state_out != NULL){
                        state_out[nstate_to_output + state_offset] = (uint32_t)tag.offset;
                        nstate_to_output += 1;
                        
                    }
                    two_users = false;


                    m_sync_state = SINGLE_USER;
                    #ifdef GRLORA_DEBUG
                    std::cout << "[mu_synchro_impl.cc] "<< "SINGLE_USER" << std::endl;
                    #endif
                    m_power1 = new_user.power;
                    user_u = new_user;
                    m_item_to_consume = mod(m_N*m_os_factor - (nitems_read(0) - tag.offset), m_N*m_os_factor);
                    user_u.cnt = 0;
                }
                else {
                    m_item_to_consume = m_samples_per_symbol;
                }

                nitems_to_output = 0;
                break;

            case SINGLE_USER:
                type = get_type(user_u.cnt);

                if (type == VOID) { // packet fully processed
                    if(!two_users){
                        if(state_out != NULL){
                            state_out[nstate_to_output+state_offset] = (uint32_t)P1_OR_P2;
                            nstate_to_output += 1;
                            
                        }
                    } 
                    m_sync_state = IDLE;
                    #ifdef GRLORA_DEBUG
                    std::cout<<"[mu_synchro_impl.cc] " << "IDLE" << std::endl;
                    #endif

                    m_item_to_consume = m_samples_per_symbol;
                    nitems_to_output = 0;

                    //reset the power variables and indicate availability with 0;
                    m_power1 = 0;
                    m_power2 = 0;
                    user_u.cnt = 0;
                }
                // accept only new user that are 3 dB below the first one //TODO need to update for case: P2 < P1 (not supported yet)
                else if (type == PAYLOAD && tags.size() == 1){// new user detected
                    if(new_user.power<((m_power1?m_power1:m_power2)-3)){//Used to avoid self-detection
                        std::cout<<RED<<"[mu_synchro_impl.cc] new user with less power detected with 3dB margin"<<RESET<<std::endl;
                        break;
                    }
                    if(!m_power1)
                        m_power1 = new_user.power;
                    else if (!m_power2)
                        m_power2 = new_user.power;
                    else
                        std::cout <<RED<<"[mu_synchro_impl.cc] ERROR: already two users"<<RESET<< std::endl;
                    user_i = new_user;
                    if(user_i.power > user_u.power){
                        if(state_out != NULL){
                            state_out[nstate_to_output+state_offset] = (uint32_t)P1_LT_P2;
                            nstate_to_output += 1;
                        }
                        two_users = true;
                        
                        m_sync_state = REALIGN_TO_NEW;
                        #ifdef GRLORA_DEBUG
                        std::cout <<"[mu_synchro_impl.cc] "<< "REALIGN_TO_NEW" << std::endl;
                        std::cout <<"[mu_synchro_impl.cc] "<< "sto_int: "<<user_i.sto_int<<" tag off "<<tags[0].offset <<" nwritten " <<nitems_written(0)<<" nread  "<<nitems_read(0)<< std::endl;
                        #endif
                        user_i.cnt = 0;
                    }
                    else{
                        m_sync_state = MULTI_USER;
                        
                        if(state_out != NULL){
                            state_out[nstate_to_output+state_offset] = (uint32_t)P1_GT_P2;
                            nstate_to_output += 1; 
                        }
                        two_users = true;
                    
                        #ifdef GRLORA_DEBUG
                        std::cout <<"[mu_synchro_impl.cc] "<< "MULTI_USER" << std::endl;
                        #endif
                        m_tau = double_mod(user_i.sto_int+user_i.sto_frac-(user_u.sto_int+user_u.sto_frac) - m_N/4,m_N);

                        // we should consider an offset before the first sample of this user
                        user_i.cnt = -1*m_tau ;
                    }

                    nitems_to_output = 0;
                    m_item_to_consume = 0;
                }
                else { // single user
                    win_len = (type == QUARTER_DOWN) ? m_N/4 : m_N;
                    add_tag(m_power1, m_power2, win_len, type, VOID, VOID, win_len, 0, offset);
                    user_u.cnt += win_len;
                    
                    m_item_to_consume = win_len * m_os_factor;
                    nitems_to_output = win_len;

                
                }
                break;

            case REALIGN_TO_NEW:
                //change polyphase
                new_poly = (user_i.sto_frac - user_u.sto_frac)*m_os_factor;

                m_tau = double_mod(user_i.sto_int+user_i.sto_frac - (user_u.sto_int+user_u.sto_frac) - m_N/4,m_N); //m_N/4 is there since one of the user is already offset by his quarter downchirp and the other not already
                win_len = (int) m_tau; //round m_tau to integer part

                delta_cfo = user_u.cfo_int+user_u.cfo_frac-user_i.cfo_int-user_i.cfo_frac;

                m_item_to_consume = m_tau * m_os_factor;
                m_tau = double_mod(m_N-m_tau,m_N); //the value of tau for the multi user state

                add_tag(m_power1>m_power2?0:m_power1, m_power1>m_power2?m_power2:0,
                        win_len, VOID,
                        VOID, get_type(user_u.cnt), m_tau, delta_cfo, offset);

                nitems_to_output = win_len ;

                user_u.cnt += win_len;

                //swap user and interferer as new user power is higher
                std::swap(user_i, user_u);
                m_sync_state = MULTI_USER;
                realign_to_new = true; //debug variable
                #ifdef GRLORA_DEBUG
                std::cout<<"[mu_synchro_impl.cc] " << "MULTI_USER" << std::endl;
                #endif
                break;

            case REALIGN_TO_PREV: //TODO verify well functioning when P2 can be smaller than P1 (not currently supported by the detector)
                win_len = (int)m_tau;
                delta_cfo = user_i.cfo_int+user_i.cfo_frac-user_u.cfo_int-user_u.cfo_frac;
                add_tag(m_power1,m_power2,win_len, VOID,get_type(user_i.cnt),
                        VOID, m_tau, delta_cfo, offset);


                m_item_to_consume = m_tau*m_os_factor;
                m_tau = m_N; //the value of tau for the single user state

                nitems_to_output = win_len;
                user_i.cnt += win_len;

                //swap user and interferer as new user power is higher
                std::swap(user_i, user_u);

                m_sync_state = SINGLE_USER;
                #ifdef GRLORA_DEBUG
                std::cout<<"[mu_synchro_impl.cc] " << "SINGLE_USER" << std::endl;
                #endif
                break;

            case MULTI_USER:
                delta_cfo = user_i.cfo_int+user_i.cfo_frac-user_u.cfo_int-user_u.cfo_frac;
                if(tags.size()>0 && nitems_read(0)!= tags[0].offset && realign_to_new){//check if realign went well
                    realign_to_new = false;
                    std::cout <<"[mu_synchro_impl.cc] ERROR: realignment failed" << std::endl;
                }
                if (get_type(user_u.cnt) == VOID){ //end of synchronized user frame
                    if(m_power1>m_power2)
                        m_power1 = 0;
                    else
                        m_power2 = 0;
                    m_sync_state = REALIGN_TO_PREV;
                    #ifdef GRLORA_DEBUG
                    std::cout <<"[mu_synchro_impl.cc] "<< "REALIGN_TO_PREV" << std::endl;
                    #endif
                    nitems_to_output = 0;
                    m_item_to_consume = 0;
                }
                else if (get_type(user_i.cnt) == VOID && user_i.cnt >= 0){// end of non-synchronized user frame
                    if(m_power1>m_power2)
                        m_power2 = 0;
                    else
                        m_power1 = 0;
                    m_sync_state = SINGLE_USER;
                    #ifdef GRLORA_DEBUG
                    std::cout <<"[mu_synchro_impl.cc] "<< "SINGLE_USER" << std::endl;
                    #endif
                    nitems_to_output = 0;
                    m_item_to_consume = 0;
                }
                else if (get_type(user_u.cnt) == QUARTER_DOWN){ // quarter downchirp of synchronized user, STO between user should be updated
                    add_tag(m_power1,m_power2, m_N/4, QUARTER_DOWN, get_type(user_i.cnt),
                            get_type(user_i.cnt + std::ceil(m_tau)),m_tau, delta_cfo, offset);
                    m_tau = double_mod(m_tau - m_N/4,m_N);
                    #ifdef GRLORA_DEBUG
                    std::cout <<"[mu_synchro_impl.cc] "<< "new tau= "<<m_tau << std::endl;
                    #endif
                    user_u.cnt += m_N/4;
                    user_i.cnt += m_N/4;
                    m_item_to_consume = m_N/4 * m_os_factor;
                    nitems_to_output = m_N/4;
                }
                else if (get_type(user_i.cnt + m_tau) == QUARTER_DOWN){// quarter downchirp of non-synchronized user, STO between user should be updated
                    // we need to get a new tau
                    m_tau = double_mod(m_tau + m_N/4,m_N);
                    add_tag(m_power1,m_power2, m_N, get_type(user_u.cnt),DOWNCHIRP,
                            get_type(user_i.cnt + std::ceil(m_tau)),m_tau, delta_cfo ,offset);
                    #ifdef GRLORA_DEBUG
                    std::cout <<"[mu_synchro_impl.cc] "<< "new tau= "<<m_tau << std::endl;
                    #endif
                    user_u.cnt += m_N;
                    user_i.cnt += m_N;
                    m_item_to_consume = m_N * m_os_factor;
                    nitems_to_output = m_N;
                }
                else{// basic two users case
                    win_len = m_N;
                    add_tag(m_power1,m_power2, win_len, get_type(user_u.cnt),get_type(user_i.cnt),
                            get_type(user_i.cnt + std::ceil(m_tau)),m_tau, delta_cfo, offset);

                    user_u.cnt += win_len;
                    user_i.cnt += win_len;
                    m_item_to_consume = win_len * m_os_factor;

                    nitems_to_output = win_len;
                }
                break;

            default:
                std::cout <<RED<< "[mu_synchro_impl.cc] ERROR: went into default case, should not happen.\n"<<RESET;

        }

        float cfo = (user_u.cfo_int + user_u.cfo_frac) / ((float) m_N);
        //copy samples to output and correct sync. user CFO
        for (size_t i = 0; i < nitems_to_output; i++) {
            out[i] = in[(i+(new_poly<0))*m_os_factor + new_poly] * gr_expj(-2*M_PI*cfo*(nitems_written(0)+i+offset));     

        }

        consume_each(m_item_to_consume);

        return std::make_tuple(m_item_to_consume, nitems_to_output, nstate_to_output);
    }

    int mu_synchro_impl::general_work (int noutput_items,
                   gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items)
    {

        #ifdef THREAD_MEASURE
        static bool m_init=false;
        if (!m_init) {
            gr::thread::thread_bind_to_processor(6);
            // gr::thread::set_thread_priority(gr::thread::get_current_thread_id(),5);
            // gr::block::set_thread_priority(5);
            const pid_t tid = syscall(SYS_gettid);
            setpriority(PRIO_PROCESS, tid, 3);
            m_init = true;
        }
        #endif
        int nitems_to_output = 0;
        int nsync_state_to_output = 0;
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];
        uint32_t *sync_state_out = NULL;
        if(output_items.size() == 2)
            sync_state_out = (uint32_t *) output_items[1];
        
        //get the number of symbols that can be processed based on the input and output buffer state
        int n_windows = std::min(ninput_items[0]/m_samples_per_symbol, noutput_items/m_N);
        
        int nitems_processed = 0;
         
        for (uint8_t i = 0; i < n_windows; i++) {
            std::tuple<int,int,int> processed_items = sync_frame(&in[nitems_processed],&out[nitems_to_output],sync_state_out, nitems_to_output,nsync_state_to_output);
            nitems_processed += std::get<0>(processed_items);
            nitems_to_output += std::get<1>(processed_items);
            nsync_state_to_output += std::get<2>(processed_items);
        }

        // Tell runtime system how many output items we produced.
        produce(0,nitems_to_output);    
        produce(1,nsync_state_to_output);    
        return WORK_CALLED_PRODUCE;
    }
  } /* namespace lora_sdr */
} /* namespace gr */
