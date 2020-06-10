#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "header_impl.h"

namespace gr {
  namespace lora_sdr {

    header::sptr
    header::make(bool impl_head, bool has_crc, uint8_t cr)
    {
      return gnuradio::get_initial_sptr
        (new header_impl(impl_head, has_crc, cr));
    }


    /*
     * The private constructor
     */
    header_impl::header_impl(bool impl_head, bool has_crc, uint8_t cr)
      : gr::block("header",
              gr::io_signature::make(1, 1, sizeof(uint8_t)),
              gr::io_signature::make(1, 1, sizeof(uint8_t)))
    {
        m_cr=cr;
        m_has_crc=has_crc;
        m_impl_head=impl_head;

        message_port_register_in(pmt::mp("msg"));
        set_msg_handler(pmt::mp("msg"),boost::bind(&header_impl::msg_handler, this, _1));
    }

    /*
     * Our virtual destructor.
     */
    header_impl::~header_impl()
    {
    }

    void
    header_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = 1;
    }
    void header_impl::msg_handler(pmt::pmt_t message){
       std::string str=pmt::symbol_to_string(message);
       m_payload_len=str.length();
    }

    int
    header_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const uint8_t *in = (const uint8_t *) input_items[0];
        uint8_t *out = (uint8_t *) output_items[0];

        if(m_impl_head){//no header to add
            memcpy(out,in,ninput_items[0]*sizeof(uint8_t));
            noutput_items = ninput_items[0];
         }
         else{//add header
            //payload length
            out[0]=(m_payload_len>>4);
            out[1]=(m_payload_len&0x0F);

            //coding rate and has_crc
            out[2]=((m_cr<<1)|m_has_crc);

            //header checksum
            bool c4=(out[0] & 0b1000)>>3 ^(out[0] & 0b0100)>>2^(out[0] & 0b0010)>>1^(out[0] & 0b0001);
            bool c3=(out[0] & 0b1000)>>3 ^(out[1] & 0b1000)>>3^(out[1] & 0b0100)>>2^(out[1] & 0b0010)>>1^(out[2] & 0b0001);
            bool c2=(out[0] & 0b0100)>>2 ^(out[1] & 0b1000)>>3^(out[1] & 0b0001)^(out[2] & 0b1000)>>3^(out[2] & 0b0010)>>1;
            bool c1=(out[0] & 0b0010)>>1 ^(out[1] & 0b0100)>>2^(out[1] & 0b0001)^(out[2] & 0b0100)>>2^(out[2] & 0b0010)>>1^(out[2] & 0b0001);
            bool c0=(out[0] & 0b0001) ^(out[1] & 0b0010)>>1^(out[2] & 0b1000)>>3^(out[2] & 0b0100)>>2^(out[2] & 0b0010)>>1^(out[2] & 0b0001);

            out[3]=c4;
            out[4]=c3<<3|c2<<2|c1<<1|c0;
            memcpy(&out[5],in,ninput_items[0]*sizeof(uint8_t));
            noutput_items = ninput_items[0] + 5;//5 beeing the header length in nibble
        }

        consume_each (ninput_items[0]);
        return noutput_items ;
    }

  } /* namespace lora */
} /* namespace gr */
