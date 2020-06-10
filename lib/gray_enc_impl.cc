#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "gray_enc_impl.h"

namespace gr {
  namespace lora_sdr {

    gray_enc::sptr
    gray_enc::make( )
    {
      return gnuradio::get_initial_sptr
        (new gray_enc_impl());
    }

    /*
     * The private constructor
     */
    gray_enc_impl::gray_enc_impl( )
      : gr::sync_block("gray_enc",
            gr::io_signature::make(1, 1, sizeof(uint32_t)),
            gr::io_signature::make(1, 1, sizeof(uint32_t)))
    {}

    /*
     * Our virtual destructor.
     */
    gray_enc_impl::~gray_enc_impl()
    {}

    int gray_enc_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
        const uint32_t *in = (const uint32_t *) input_items[0];
        uint32_t *out = (uint32_t *) output_items[0];
        for(int i=0; i<noutput_items;i++){
            out[i]= (in[i] ^ (in[i] >> 1u));
            #ifdef GRLORA_DEBUG
            std::cout<<std::hex<<"0x"<<in[i]<<" ---> "<<"0x"<<out[i]<<std::dec<<std::endl;
            #endif
        }
    return noutput_items;
    }
  } /* namespace lora */
} /* namespace gr */
