#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "frame_sync_impl.h"

namespace gr {
  namespace lora_sdr {

    frame_sync::sptr
    frame_sync::make(float samp_rate, uint32_t bandwidth, uint8_t sf, bool impl_head)
    {
      return gnuradio::get_initial_sptr
        (new frame_sync_impl(samp_rate, bandwidth, sf, impl_head));
    }

    /*
     * The private constructor
     */
    frame_sync_impl::frame_sync_impl(float samp_rate, uint32_t bandwidth, uint8_t sf, bool impl_head)
      : gr::block("frame_sync",
      gr::io_signature::make(1, 1, sizeof(gr_complex)),
      gr::io_signature::make(0, 1, (1u << sf)*sizeof(gr_complex)))
      {
        m_state             = DETECT;
        m_bw                = bandwidth;
        m_samp_rate         = samp_rate;
        m_sf                = sf;
        symbols_to_skip     = 4;
        n_up                = 8;
        net_id_1            = 8; // should be different from 2^sf-1, 0 and 1
        net_id_2            = 16;
        up_symb_to_use         = 6;

        usFactor = 4;
        lambda_sto = 0;

        m_impl_head = impl_head;

        m_number_of_bins     = (uint32_t)(1u << m_sf);
        m_samples_per_symbol = (uint32_t)(m_samp_rate * m_number_of_bins/ m_bw);

        m_upchirp.resize(m_samples_per_symbol);
        m_downchirp.resize(m_samples_per_symbol);
        preamble_up.resize(n_up*m_samples_per_symbol);
        CFO_frac_correc.resize(m_samples_per_symbol);
        symb_corr.resize(m_samples_per_symbol);
        in_down.resize(m_number_of_bins);
        preamble_raw.resize(n_up*m_samples_per_symbol);

        build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

        bin_idx = 0;
        symbol_cnt = 1;
        k_hat = 0;

        cx_in = new kiss_fft_cpx[m_samples_per_symbol];
        cx_out = new kiss_fft_cpx[m_samples_per_symbol];
        //register message ports
        message_port_register_out(pmt::mp("new_frame"));

        message_port_register_in(pmt::mp("CR"));
        set_msg_handler(pmt::mp("CR"),boost::bind(&frame_sync_impl::header_cr_handler, this, _1));

        message_port_register_in(pmt::mp("pay_len"));
        set_msg_handler(pmt::mp("pay_len"),boost::bind(&frame_sync_impl::header_pay_len_handler, this, _1));

        message_port_register_in(pmt::mp("crc"));
        set_msg_handler(pmt::mp("crc"),boost::bind(&frame_sync_impl::header_crc_handler, this, _1));

        message_port_register_in(pmt::mp("err"));
        set_msg_handler(pmt::mp("err"),boost::bind(&frame_sync_impl::header_err_handler, this, _1));

        message_port_register_in(pmt::mp("frame_err"));
        set_msg_handler(pmt::mp("frame_err"),boost::bind(&frame_sync_impl::frame_err_handler, this, _1));
        #ifdef GRLORA_MEASUREMENTS
        int num = 0;//check next file name to use
        while(1){
            std::ifstream infile("../matlab/measurements/sync"+std::to_string(num)+".txt");
             if(!infile.good())
                break;
            num++;
        }
        sync_log.open("../matlab/measurements/sync"+std::to_string(num)+".txt", std::ios::out | std::ios::trunc );
        #endif
        #ifdef GRLORA_DEBUG
        numb_symbol_to_save=80;//number of symbol per erroneous frame to save
        last_frame.resize(m_samples_per_symbol*numb_symbol_to_save);
        samples_file.open("../matlab/err_symb.txt", std::ios::out | std::ios::trunc );
        #endif
    }

    /*
     * Our virtual destructor.
     */
    frame_sync_impl::~frame_sync_impl()
    {}

    void frame_sync_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required){
        ninput_items_required[0] = usFactor*(m_samples_per_symbol+2);
    }

    void frame_sync_impl::estimate_CFO(gr_complex* samples){
        int k0;
        double Y_1, Y0, Y1, u, v, ka, wa, k_residual;
        std::vector<gr_complex> CFO_frac_correc_aug(up_symb_to_use*m_number_of_bins); ///< CFO frac correction vector
        std::vector<gr_complex> dechirped(up_symb_to_use*m_number_of_bins);
        kiss_fft_cpx* cx_in_cfo = new kiss_fft_cpx[2*up_symb_to_use*m_samples_per_symbol];
        kiss_fft_cpx* cx_out_cfo = new kiss_fft_cpx[2*up_symb_to_use*m_samples_per_symbol];

        float fft_mag_sq[2*up_symb_to_use*m_number_of_bins];
        kiss_fft_cfg cfg_cfo =  kiss_fft_alloc(2*up_symb_to_use*m_samples_per_symbol,0,0,0);
        //create longer downchirp
        std::vector<gr_complex> downchirp_aug(up_symb_to_use*m_number_of_bins);
        for (int i = 0; i < up_symb_to_use; i++) {
            memcpy(&downchirp_aug[i*m_number_of_bins],&m_downchirp[0],m_number_of_bins*sizeof(gr_complex));
        }

        //Dechirping
        volk_32fc_x2_multiply_32fc(&dechirped[0],samples,&downchirp_aug[0],up_symb_to_use*m_samples_per_symbol);
        //prepare FFT
        for (int i = 0; i < 2*up_symb_to_use*m_samples_per_symbol; i++) {
            if(i<up_symb_to_use*m_samples_per_symbol){
                cx_in_cfo[i].r = dechirped[i].real();
                cx_in_cfo[i].i = dechirped[i].imag();
            }
            else{//add padding
                cx_in_cfo[i].r = 0;
                cx_in_cfo[i].i = 0;
            }
        }
        //do the FFT
        kiss_fft(cfg_cfo,cx_in_cfo,cx_out_cfo);
        // Get magnitude
        for (uint32_t i = 0u; i < 2*up_symb_to_use*m_samples_per_symbol; i++) {
            fft_mag_sq[i] = cx_out_cfo[i].r*cx_out_cfo[i].r+cx_out_cfo[i].i*cx_out_cfo[i].i;
        }
        free(cfg_cfo);
        // get argmax here
        k0 = ((std::max_element(fft_mag_sq, fft_mag_sq + 2*up_symb_to_use*m_number_of_bins) - fft_mag_sq));

        // get three spectral lines
        Y_1 = fft_mag_sq[mod(k0-1,2*up_symb_to_use*m_number_of_bins)];
        Y0 = fft_mag_sq[k0];
        Y1 = fft_mag_sq[mod(k0+1,2*up_symb_to_use*m_number_of_bins)];
        //set constant coeff
        u = 64*m_number_of_bins/406.5506497; //from Cui yang (15)
        v = u*2.4674;
        //RCTSL
        wa = (Y1-Y_1)/(u*(Y1+Y_1)+v*Y0);
        ka = wa*m_number_of_bins/M_PI;
        k_residual = fmod((k0+ka)/2/up_symb_to_use,1);
        lambda_cfo = k_residual - (k_residual>0.5?1:0);
        // Correct CFO in preamble
        for (int n = 0; n < up_symb_to_use*m_number_of_bins; n++) {
            CFO_frac_correc_aug[n]= gr_expj(-2* M_PI *lambda_cfo/m_number_of_bins*n) ;
        }
        volk_32fc_x2_multiply_32fc(&preamble_up[0],samples,&CFO_frac_correc_aug[0],up_symb_to_use*m_number_of_bins);
    }
    void frame_sync_impl::estimate_CFO_Bernier(){
        int k0[m_number_of_bins];
        double k0_mag[m_number_of_bins];
        std::vector<gr_complex> fft_val(up_symb_to_use*m_number_of_bins);

        std::vector<gr_complex> dechirped(m_number_of_bins);
        kiss_fft_cpx* cx_in_cfo = new kiss_fft_cpx[m_samples_per_symbol];
        kiss_fft_cpx* cx_out_cfo = new kiss_fft_cpx[m_samples_per_symbol];
        float fft_mag_sq[m_number_of_bins];
        for (size_t i = 0; i < m_number_of_bins; i++) {
            fft_mag_sq[i] = 0;
        }
        kiss_fft_cfg cfg_cfo = kiss_fft_alloc(m_samples_per_symbol,0,0,0);

        for (int i = 0; i < up_symb_to_use; i++) {
            //Dechirping
            volk_32fc_x2_multiply_32fc(&dechirped[0],&preamble_raw[(m_number_of_bins-k_hat)+m_number_of_bins*i],&m_downchirp[0],m_samples_per_symbol);
            //prepare FFT
            for (int i = 0; i < m_samples_per_symbol; i++) {
                cx_in_cfo[i].r = dechirped[i].real();
                cx_in_cfo[i].i = dechirped[i].imag();
            }
            //do the FFT
            kiss_fft(cfg_cfo,cx_in_cfo,cx_out_cfo);
            // Get magnitude

            for (uint32_t j = 0u; j < m_samples_per_symbol; j++) {
                fft_mag_sq[j] = cx_out_cfo[j].r*cx_out_cfo[j].r+cx_out_cfo[j].i*cx_out_cfo[j].i;
                fft_val[j+i*m_samples_per_symbol] = gr_complex(cx_out_cfo[j].r, cx_out_cfo[j].i);
            }
            k0[i] = std::max_element(fft_mag_sq, fft_mag_sq + m_number_of_bins) - fft_mag_sq;

            k0_mag[i] = fft_mag_sq[k0[i]];
        }
        free(cfg_cfo);
        // get argmax
        int idx_max = k0[std::max_element(k0_mag, k0_mag + m_number_of_bins) - k0_mag];

        gr_complex four_cum(0.0f, 0.0f);
        for (int i = 0; i < up_symb_to_use-1; i++) {
            four_cum+=fft_val[idx_max+m_number_of_bins*i]*std::conj(fft_val[idx_max+m_number_of_bins*(i+1)]);
        }
        lambda_bernier=-std::arg(four_cum)/2/M_PI;
    }

    void frame_sync_impl::estimate_STO(){
        int k0;
        double Y_1, Y0, Y1, u, v, ka, wa, k_residual;

        std::vector<gr_complex> dechirped(m_number_of_bins);
        kiss_fft_cpx* cx_in_cfo = new kiss_fft_cpx[2*m_samples_per_symbol];
        kiss_fft_cpx* cx_out_cfo = new kiss_fft_cpx[2*m_samples_per_symbol];

        float fft_mag_sq[2*m_number_of_bins];
        for (size_t i = 0; i < 2*m_number_of_bins; i++) {
            fft_mag_sq[i] = 0;
        }
        kiss_fft_cfg cfg_cfo =  kiss_fft_alloc(2*m_samples_per_symbol,0,0,0);

        for (int i = 0; i < up_symb_to_use; i++) {
            //Dechirping
            volk_32fc_x2_multiply_32fc(&dechirped[0],&preamble_up[m_number_of_bins*i],&m_downchirp[0],m_samples_per_symbol);
            //prepare FFT
            for (int i = 0; i < 2*m_samples_per_symbol; i++) {
                if(i<m_samples_per_symbol){
                    cx_in_cfo[i].r = dechirped[i].real();
                    cx_in_cfo[i].i = dechirped[i].imag();
                }
                else{//add padding
                    cx_in_cfo[i].r = 0;
                    cx_in_cfo[i].i = 0;
                }
            }
            //do the FFT
            kiss_fft(cfg_cfo,cx_in_cfo,cx_out_cfo);
            // Get magnitude
            for (uint32_t i = 0u; i < 2*m_samples_per_symbol; i++) {
                fft_mag_sq[i] += cx_out_cfo[i].r*cx_out_cfo[i].r+cx_out_cfo[i].i*cx_out_cfo[i].i;
            }
        }
        free(cfg_cfo);

        // get argmax here
        k0 = std::max_element(fft_mag_sq, fft_mag_sq + 2*m_number_of_bins) - fft_mag_sq;

        // get three spectral lines
        Y_1 = fft_mag_sq[mod(k0-1,2*m_number_of_bins)];
        Y0 = fft_mag_sq[k0];
        Y1 = fft_mag_sq[mod(k0+1,2*m_number_of_bins)];
        //set constant coeff
        u = 64*m_number_of_bins/406.5506497; //from Cui yang (eq.15)
        v = u*2.4674;
        //RCTSL
        wa = (Y1-Y_1)/(u*(Y1+Y_1)+v*Y0);
        ka = wa*m_number_of_bins/M_PI;
        k_residual = fmod((k0+ka)/2,1);
        lambda_sto = k_residual - (k_residual>0.5?1:0);
    }

    uint32_t frame_sync_impl::get_symbol_val(const gr_complex *samples, gr_complex *ref_chirp) {
        double sig_en=0;
        float fft_mag[m_number_of_bins];
        std::vector<gr_complex> dechirped(m_number_of_bins);

        kiss_fft_cfg cfg =  kiss_fft_alloc(m_samples_per_symbol,0,0,0);

        // Multiply with ideal downchirp
        volk_32fc_x2_multiply_32fc(&dechirped[0],samples,ref_chirp,m_samples_per_symbol);

        for (int i = 0; i < m_samples_per_symbol; i++) {
          cx_in[i].r = dechirped[i].real();
          cx_in[i].i = dechirped[i].imag();
        }
        //do the FFT
        kiss_fft(cfg,cx_in,cx_out);

        // Get magnitude
        for (uint32_t i = 0u; i < m_number_of_bins; i++) {
            fft_mag[i] = cx_out[i].r*cx_out[i].r+cx_out[i].i*cx_out[i].i;
            sig_en+=fft_mag[i];
        }
        free(cfg);
        // Return argmax here
        return ((std::max_element(fft_mag, fft_mag + m_number_of_bins) - fft_mag));
    }

    float frame_sync_impl::determine_energy(const gr_complex *samples) {
            float magsq_chirp[m_samples_per_symbol];
            float energy_chirp = 0;
            volk_32fc_magnitude_squared_32f(magsq_chirp, samples, m_samples_per_symbol);
            volk_32f_accumulator_s32f(&energy_chirp, magsq_chirp, m_samples_per_symbol);
            return energy_chirp;
        }
    void frame_sync_impl::header_cr_handler(pmt::pmt_t cr){
        m_cr = pmt::to_long(cr);
        received_cr = true;
        if(received_cr&&received_crc&&received_pay_len)//get number of symbol of the frame
            symb_numb = 8 + ceil((double)(2*m_pay_len-m_sf+2+!m_impl_head*5+m_has_crc*4)/m_sf)*(4+m_cr);
    };
    void frame_sync_impl::header_pay_len_handler(pmt::pmt_t pay_len){
        m_pay_len = pmt::to_long(pay_len);
        received_pay_len = true;
        if(received_cr&&received_crc&&received_pay_len)//get number of symbol of the frame
            symb_numb = 8 + ceil((double)(2*m_pay_len-m_sf+2+!m_impl_head*5+m_has_crc*4)/m_sf)*(4+m_cr);
    };
    void frame_sync_impl::header_crc_handler(pmt::pmt_t crc){
        m_has_crc = pmt::to_long(crc);
        received_crc = true;
        if(received_cr&&received_crc&&received_pay_len)//get number of symbol of the frame
            symb_numb = 8 + ceil((double)(2*m_pay_len-m_sf+2+!m_impl_head*5+m_has_crc*4)/m_sf)*(4+m_cr);
    };
    void frame_sync_impl::header_err_handler(pmt::pmt_t err){
        m_state = DETECT;
        symbol_cnt = 1;
    };
    void frame_sync_impl::frame_err_handler(pmt::pmt_t err){
        #ifdef GRLORA_DEBUG
        for(int j=0;j<numb_symbol_to_save;j++){
            for(int i=0;i<m_number_of_bins;i++)
                samples_file<<last_frame[i+m_number_of_bins*j].real()<<(last_frame[i+m_number_of_bins*j].imag()<0?"-":"+")<<std::abs(last_frame[i+m_number_of_bins*j].imag()) <<"i,";
        samples_file<<std::endl;
        }
        std::cout << "saved one frame" << '\n';
        #endif
    };

    int
    frame_sync_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];

        //downsampling
        for (int ii=0;ii<m_number_of_bins;ii++)
            in_down[ii]=in[(int)(usFactor-1+usFactor*ii-round(lambda_sto*usFactor))];
        switch (m_state) {
          case DETECT: {
              bin_idx_new = get_symbol_val(&in_down[0], &m_downchirp[0]);

              if(std::abs(bin_idx_new-bin_idx)<=1){//look for consecutive reference upchirps(with a margin of ±1)
                  if(symbol_cnt==1)//we should also add the first symbol value
                      k_hat+=bin_idx;

                  k_hat+=bin_idx_new;
                  memcpy(&preamble_raw[m_samples_per_symbol*symbol_cnt],&in_down[0],m_samples_per_symbol*sizeof(gr_complex));
                  symbol_cnt++;
              }
              else{
                  memcpy(&preamble_raw[0],&in_down[0],m_samples_per_symbol*sizeof(gr_complex));
                  symbol_cnt = 1;
                  k_hat = 0;
              }
              bin_idx = bin_idx_new;
              if(symbol_cnt == (int)(n_up-1)){
                  m_state = SYNC;
                  symbol_cnt = 0;
                  cfo_sto_est = false;

                  k_hat = round(k_hat/(n_up-1));

                  //perform the coarse synchronization
                  items_to_consume = usFactor*(m_samples_per_symbol-k_hat);
              }
              else
                  items_to_consume = usFactor*m_samples_per_symbol;
              noutput_items = 0;
              break;
          }
          case SYNC:{
              if(!cfo_sto_est){
                  estimate_CFO(&preamble_raw[m_number_of_bins-k_hat]);
                  estimate_STO();
                  //create correction vector
                  for (int n = 0; n< m_number_of_bins; n++) {
                      CFO_frac_correc[n]= gr_expj(-2* M_PI *lambda_cfo/m_number_of_bins*n) ;
                  }
                  cfo_sto_est=true;
              }
              items_to_consume = usFactor*m_samples_per_symbol;
              //apply cfo correction
              volk_32fc_x2_multiply_32fc(&symb_corr[0],&in_down[0],&CFO_frac_correc[0],m_samples_per_symbol);

              bin_idx = get_symbol_val(&symb_corr[0], &m_downchirp[0]);

              switch (symbol_cnt) {
                  case NET_ID1:{
                        if(bin_idx==0||bin_idx==1||bin_idx==m_number_of_bins-1){// look for additional upchirps. Won't work if network identifier 1 equals 2^sf-1, 0 or 1!
                        }
                        else if (abs(bin_idx-net_id_1)>1){ //wrong network identifier
                            m_state = DETECT;
                            symbol_cnt = 1;
                            noutput_items = 0;
                            k_hat = 0;
                            lambda_sto = 0;
                        }
                        else { //network identifier 1 correct or off by one
                            net_id_off=bin_idx-net_id_1;
                            symbol_cnt = NET_ID2;
                        }
                        break;
                    }
                    case NET_ID2:{
                        if (abs(bin_idx-net_id_2)>1){ //wrong network identifier
                            m_state = DETECT;
                            symbol_cnt = 1;
                            noutput_items = 0;
                            k_hat = 0;
                            lambda_sto = 0;
                        }
                        else if(net_id_off && (bin_idx-net_id_2)==net_id_off){//correct case off by one net id
                            #ifdef GRLORA_MEASUREMENTS
                            off_by_one_id=1;
                            #endif

                            items_to_consume-=usFactor*net_id_off;
                            symbol_cnt = DOWNCHIRP1;
                        }
                        else{
                            #ifdef GRLORA_MEASUREMENTS
                            off_by_one_id=0;
                            #endif
                            symbol_cnt = DOWNCHIRP1;
                        }
                        break;
                    }
                    case DOWNCHIRP1:
                        symbol_cnt = DOWNCHIRP2;
                        break;
                    case DOWNCHIRP2:{
                        down_val = get_symbol_val(&symb_corr[0], &m_upchirp[0]);
                        symbol_cnt = QUARTER_DOWN;
                        break;
                    }
                    case QUARTER_DOWN:{
                        if (down_val<m_number_of_bins/2){
                            CFOint = floor(down_val/2);
                            message_port_pub(pmt::intern("new_frame"),pmt::mp((long)CFOint));
                        }
                        else{
                            CFOint = ceil(double(down_val-(int)m_number_of_bins)/2);
                            message_port_pub(pmt::intern("new_frame"),pmt::mp((long)((m_number_of_bins+CFOint)%m_number_of_bins)));
                        }
                        items_to_consume = usFactor*m_samples_per_symbol/4+usFactor*CFOint;
                        symbol_cnt = 0;
                        m_state = FRAC_CFO_CORREC;
                        #ifdef GRLORA_MEASUREMENTS
                        sync_log<<std::endl<<lambda_cfo<<", "<<lambda_sto<<", "<<CFOint<<","<<off_by_one_id<<","<<lambda_bernier<<",";
                        #endif
                    }
                }
              noutput_items = 0;
              break;
          }
          case FRAC_CFO_CORREC:{
              //transmitt only useful symbols (at least 8 symbol)
              if(symbol_cnt<symb_numb||!(received_cr&&received_crc&&received_pay_len)){
                  //apply fractional cfo correction
                  volk_32fc_x2_multiply_32fc(out,&in_down[0],&CFO_frac_correc[0],m_samples_per_symbol);
                  #ifdef GRLORA_MEASUREMENTS
                  sync_log<< std::fixed<<std::setprecision(10)<<determine_energy(&in_down[0])<<",";
                  #endif
                  #ifdef GRLORA_DEBUG
                  if(symbol_cnt<numb_symbol_to_save)
                    memcpy(&last_frame[symbol_cnt*m_number_of_bins],&in_down[0],m_samples_per_symbol*sizeof(gr_complex));
                  #endif
                  items_to_consume = usFactor*m_samples_per_symbol;
                  noutput_items = 1;
                  symbol_cnt++;
              }
              else{
                      m_state = DETECT;
                      symbol_cnt = 1;
                      items_to_consume = usFactor*m_samples_per_symbol;
                      noutput_items = 0;
                      k_hat = 0;
                      lambda_sto = 0;
              }
              break;
          }
          default: {
              std::cerr << "[LoRa sync] WARNING : No state! Shouldn't happen\n";
              break;
          }
        }
        consume_each(items_to_consume);
        return noutput_items;
      }
  } /* namespace lora_sdr */
} /* namespace gr */
