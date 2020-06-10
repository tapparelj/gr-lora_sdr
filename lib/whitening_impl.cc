

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "whitening_impl.h"
#include "tables.h"

namespace gr {
  namespace lora_sdr {

    whitening::sptr
    whitening::make( )
    {
      return gnuradio::get_initial_sptr
        (new whitening_impl());
    }


    /*
     * The private constructor
     */
    whitening_impl::whitening_impl( )
      : gr::sync_block("whitening",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 1, sizeof(uint8_t)))
    {
        new_message = false;

        message_port_register_in(pmt::mp("msg"));
        set_msg_handler(pmt::mp("msg"), // This is the port identifier
        boost::bind(&whitening_impl::msg_handler, this, _1));
    }

    /*
     * Our virtual destructor.
     */
    whitening_impl::~whitening_impl()
    {}
    void whitening_impl::msg_handler(pmt::pmt_t message){
       std::string str=pmt::symbol_to_string(message);
       std::copy(str.begin(), str.end(), std::back_inserter(m_payload));
       new_message = true;
    }

    int whitening_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
        if(new_message){

            uint8_t *out = (uint8_t *) output_items[0];

            for(uint i=0;i<m_payload.size();i++){
                out[2*i]=(m_payload[i] ^whitening_seq[i]) & 0x0F;
                out[2*i+1]=(m_payload[i]^whitening_seq[i])>>4;
            }

            noutput_items=2*m_payload.size();
            m_payload.clear();
            new_message=false;
        }
        else
            noutput_items=0;
        return noutput_items;
    }

  } /* namespace lora */
} /* namespace gr */
