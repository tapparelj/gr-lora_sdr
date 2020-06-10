#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "interleaver_impl.h"
#include <lora_sdr/utilities.h>

namespace gr {
  namespace lora_sdr {

    interleaver::sptr
    interleaver::make(uint8_t cr, uint8_t sf)
    {
      return gnuradio::get_initial_sptr
        (new interleaver_impl(cr, sf));
    }


    /*
     * The private constructor
     */
    interleaver_impl::interleaver_impl(uint8_t cr, uint8_t sf)
      : gr::block("interleaver",
              gr::io_signature::make(1, 1, sizeof(uint8_t)),
              gr::io_signature::make(1, 1, sizeof(uint32_t)))
    {
        m_sf=sf;
        m_cr=cr;

        cw_cnt=0;

        message_port_register_in(pmt::mp("msg"));
        set_msg_handler(pmt::mp("msg"),boost::bind(&interleaver_impl::msg_handler, this, _1));
    }

    /*
     * Our virtual destructor.
     */
    interleaver_impl::~interleaver_impl()
    {
    }

    void
    interleaver_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = 1;
    }
    void interleaver_impl::msg_handler(pmt::pmt_t message){
        cw_cnt=0;
    }

    int
    interleaver_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const uint8_t *in = (const uint8_t *) input_items[0];
        uint32_t *out = (uint32_t *) output_items[0];

        uint8_t ppm = 4+((cw_cnt<m_sf-2)?4:m_cr);
        uint8_t sf_app = (cw_cnt<m_sf-2)?m_sf-2:m_sf;

        //Create the empty matrices
        std::vector<std::vector<bool>> cw_bin(sf_app);
        std::vector<bool> init_bit(m_sf,0);
        std::vector<std::vector<bool>> inter_bin(ppm,init_bit);

        //convert to input codewords to binary vector of vector
        for(int i=0;i<sf_app;i++){
         if(i>=ninput_items[0])
            cw_bin[i]=int2bool(0,ppm);
         else
          cw_bin[i]=int2bool(in[i],ppm);
          cw_cnt++;
        }

        #ifdef GRLORA_DEBUG
        std::cout<<"codewords---- "<<std::endl;
        for (uint32_t i =0u ; i<sf_app ;i++){
            for(int j=0;j<int(ppm);j++){
                std::cout<<cw_bin[i][j];
            }
            std::cout<<" 0x"<<std::hex<<(int)in[i]<<std::dec<< std::endl;
        }
        std::cout<<std::endl;
        #endif
         //Do the actual interleaving
        for (int32_t i = 0; i < ppm ; i++) {
            for (int32_t j = 0; j < int(sf_app); j++) {
                    inter_bin[i][j] = cw_bin[mod((i-j-1),sf_app)][i];
            }
            //For the first bloc we add a parity bit and a zero in the end of the lora symbol(reduced rate)
            if(cw_cnt == m_sf-2)
              inter_bin[i][sf_app] = accumulate(inter_bin[i].begin(), inter_bin[i].end(),0)%2;

            out[i]=bool2int(inter_bin[i]);
        }

         #ifdef GRLORA_DEBUG
        std::cout<<"interleaved------"  <<std::endl;
        for (uint32_t i =0u ; i<ppm ;i++){
            for(int j=0;j<int(m_sf);j++){
                std::cout<<inter_bin[i][j];
            }
            std::cout<<" "<<out[i]<< std::endl;
        }
        std::cout<<std::endl;
        #endif
        consume_each (ninput_items[0]>sf_app?sf_app:ninput_items[0]);

        return ppm;

    }

  } /* namespace lora */
} /* namespace gr */
