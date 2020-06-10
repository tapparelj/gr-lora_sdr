#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "deinterleaver_impl.h"
#include <lora_sdr/utilities.h>

namespace gr {
  namespace lora_sdr {

    deinterleaver::sptr
    deinterleaver::make(uint8_t sf)
    {
    return gnuradio::get_initial_sptr
        (new deinterleaver_impl(sf));
    }

    /*
    * The private constructor
    */
    deinterleaver_impl::deinterleaver_impl(uint8_t sf)
    : gr::block("deinterleaver",
            gr::io_signature::make(1, 1, sizeof(uint32_t)),
            gr::io_signature::make(1, 1, sizeof(uint8_t)))
    {
        is_first=true;
        m_sf=sf;
        message_port_register_in(pmt::mp("CR"));
        set_msg_handler(pmt::mp("CR"),boost::bind(&deinterleaver_impl::header_cr_handler, this, _1));
        message_port_register_in(pmt::mp("new_frame"));
        set_msg_handler(pmt::mp("new_frame"),boost::bind(&deinterleaver_impl::new_frame_handler, this, _1));
    }

    /*
    * Our virtual destructor.
    */
    deinterleaver_impl::~deinterleaver_impl()
    {}

    void deinterleaver_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        ninput_items_required[0] = 4;
    }

    void deinterleaver_impl::new_frame_handler(pmt::pmt_t id){
        is_first = true;
    }
    void deinterleaver_impl::header_cr_handler(pmt::pmt_t cr){
        m_cr = pmt::to_long(cr);
    };

    int deinterleaver_impl::general_work (int noutput_items,
                    gr_vector_int &ninput_items,
                    gr_vector_const_void_star &input_items,
                    gr_vector_void_star &output_items)
    {
        const uint32_t *in = (uint32_t *) input_items[0];
        uint8_t *out = (uint8_t *) output_items[0];
        sf_app = is_first?m_sf-2:m_sf;//Use reduced rate for the first block
        cw_len = is_first?8:m_cr+4;
        if(ninput_items[0]>=cw_len){//wait for a full block to deinterleave
            //Create the empty matrices
            std::vector<std::vector<bool>> inter_bin(cw_len);
            std::vector<bool> init_bit(cw_len,0);
            std::vector<std::vector<bool>> deinter_bin(sf_app,init_bit);

            //convert decimal vector to binary vector of vector
            for (int i=0 ; i<cw_len ; i++){
                inter_bin[i]=int2bool(in[i],sf_app);
            }
            #ifdef GRLORA_DEBUG
            std::cout<<"interleaved----"  <<std::endl;
            for (uint32_t i =0u ; i<cw_len ;i++){
                for(int j=0;j<int(sf_app);j++){
                    std::cout<<inter_bin[i][j];
                }
                std::cout<<" "<<(int)in[i]<< std::endl;
            }
            std::cout<<std::endl;
            #endif
            //Do the actual deinterleaving
            for (int32_t i = 0; i < cw_len ; i++) {
                for (int32_t j = 0; j < int(sf_app); j++) {
                        deinter_bin[mod((i-j-1),sf_app)][i]= inter_bin[i][j];
                }
            }
            //transform codewords from binary vector to dec
            for(uint i=0;i<sf_app;i++){
                out[i]=bool2int(deinter_bin[i]);
            }

            #ifdef GRLORA_DEBUG
            std::cout<<"codewords----"  <<std::endl;
            for (uint32_t i =0u ; i<sf_app ;i++){
                for(int j=0;j<int(cw_len);j++){
                    std::cout<<deinter_bin[i][j];
                }
                std::cout<<" 0x"<<std::hex<<(int)out[i]<<std::dec<< std::endl;
            }
            std::cout<<std::endl;
            #endif

            consume_each(is_first?8:m_cr+4);
            is_first=false;
            return sf_app;
        }
    }
  } /* namespace lora */
} /* namespace gr */
