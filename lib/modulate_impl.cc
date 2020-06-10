#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "modulate_impl.h"

namespace gr {
  namespace lora_sdr {

    modulate::sptr
    modulate::make(uint8_t sf, uint32_t samp_rate, uint32_t bw)
    {
      return gnuradio::get_initial_sptr
        (new modulate_impl(sf, samp_rate, bw));
    }
    /*
     * The private constructor
     */
    modulate_impl::modulate_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw)
      : gr::block("modulate",
              gr::io_signature::make(1, 1, sizeof(uint32_t)),
              gr::io_signature::make(1,1, sizeof(gr_complex)))
    {

        m_sf=sf;
        m_samp_rate=samp_rate;
        m_bw=bw;

        m_number_of_bins    =(uint32_t)(1u << m_sf);
        m_symbols_per_second = (double)m_bw/m_number_of_bins;
        m_samples_per_symbol = (uint32_t)(m_samp_rate / m_symbols_per_second);

        m_downchirp.resize(m_samples_per_symbol);
        m_upchirp.resize(m_samples_per_symbol);

        build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

        n_up = 8;
        symb_cnt = 0;
        message_port_register_in(pmt::mp("msg"));
        set_msg_handler(pmt::mp("msg"),boost::bind(&modulate_impl::msg_handler, this, _1));
    }

    /*
     * Our virtual destructor.
     */
    modulate_impl::~modulate_impl()
    {}

    void
    modulate_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = 1;
    }
    void modulate_impl::msg_handler(pmt::pmt_t message){
        symb_cnt=0;
    }

    int modulate_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const uint32_t *in = (const uint32_t *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];

        noutput_items = m_samples_per_symbol;
        uint i=0;

        if(symb_cnt<n_up+4.25){//send preamble
            if(symb_cnt==0){//offset
                uint off=0;
                memcpy(&out[0],&m_upchirp[0],m_samples_per_symbol*sizeof(gr_complex));
                noutput_items = m_samples_per_symbol+off;
            }
            else if(symb_cnt<n_up){//upchirps
                memcpy(&out[0],&m_upchirp[0],m_samples_per_symbol*sizeof(gr_complex));
            }
            else if(symb_cnt==n_up){// network identifier 1
                build_upchirp(&out[0],8,m_sf);
            }
            else if(symb_cnt==n_up+1){// network identifier 2
                build_upchirp(&out[0],16,m_sf);
            }
            else if(symb_cnt<n_up+4){//downchirps
                memcpy(&out[0],&m_downchirp[0],m_samples_per_symbol*sizeof(gr_complex));
            }
            else{//quarter of downchirp
                memcpy(&out[0],&m_downchirp[0],m_samples_per_symbol/4*sizeof(gr_complex));
                noutput_items = m_samples_per_symbol/4;
            }
        }
        else{//payload
            build_upchirp(&out[0],in[0],m_sf);
            consume_each(1);
        }
        symb_cnt++;
        return(noutput_items);
    }

  } /* namespace lora */
} /* namespace gr */
