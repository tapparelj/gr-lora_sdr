
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "header_decoder_impl.h"

namespace gr {
  namespace lora_sdr {

    header_decoder::sptr
    header_decoder::make(bool impl_head, uint8_t cr, uint32_t pay_len, bool has_crc)
    {
      return gnuradio::get_initial_sptr
        (new header_decoder_impl(impl_head, cr, pay_len, has_crc));
    }

    /*
     * The private constructor
     */
    header_decoder_impl::header_decoder_impl(bool impl_head, uint8_t cr, uint32_t pay_len, bool has_crc)
      : gr::block("header_decoder",
              gr::io_signature::make(1, 1, sizeof(uint8_t)),
              gr::io_signature::make(1, 1, sizeof(uint8_t)))
    {
        m_impl_header = impl_head;
        m_cr = cr;
        m_payload_len = pay_len;
        m_has_crc = has_crc;

        is_first = true;
        pay_cnt = 0;

        message_port_register_in(pmt::mp("new_frame"));
        set_msg_handler(pmt::mp("new_frame"),boost::bind(&header_decoder_impl::new_frame_handler, this, _1));

        message_port_register_out(pmt::mp("CR"));
        message_port_register_out(pmt::mp("pay_len"));
        message_port_register_out(pmt::mp("CRC"));
        message_port_register_out(pmt::mp("err"));
    }
    /*
     * Our virtual destructor.
     */
    header_decoder_impl::~header_decoder_impl()
    {
    }

    void
    header_decoder_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }
    void header_decoder_impl::new_frame_handler(pmt::pmt_t id){
        is_first = true;
        pay_cnt = 0;
    }

    int header_decoder_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const uint8_t *in = (const uint8_t *) input_items[0];
      uint8_t *out = (uint8_t *) output_items[0];
      nout = 0;
      if(is_first){
        if(m_impl_header){//implicit header, all parameters should have been provided
            message_port_pub(pmt::intern("CR"),pmt::mp(m_cr));
            message_port_pub(pmt::intern("CRC"),pmt::mp(m_has_crc));
            message_port_pub(pmt::intern("pay_len"),pmt::mp(m_payload_len));

            for(int i=0;i<ninput_items[0];i++){
                //only output payload or CRC
                if(pay_cnt<m_payload_len*2+(m_has_crc?4:0)){
                    out[i]=in[i];
                    pay_cnt++;
                }
            }
            is_first=false;
            consume_each (ninput_items[0]);
            return pay_cnt;
        }
        else{//explicit header to decode
            std::cout<<"--------Header--------"<<std::endl;
            m_payload_len=(in[0]<<4)+in[1];
            m_has_crc=in[2] & 1;
            m_cr = in[2]>>1;

            header_chk= ((in[3] & 1)<<4) + in[4];

            //check header Checksum
            bool c4=(in[0] & 0b1000)>>3 ^(in[0] & 0b0100)>>2^(in[0] & 0b0010)>>1^(in[0] & 0b0001);
            bool c3=(in[0] & 0b1000)>>3 ^(in[1] & 0b1000)>>3^(in[1] & 0b0100)>>2^(in[1] & 0b0010)>>1^(in[2] & 0b0001);
            bool c2=(in[0] & 0b0100)>>2 ^(in[1] & 0b1000)>>3^(in[1] & 0b0001)^(in[2] & 0b1000)>>3^(in[2] & 0b0010)>>1;
            bool c1=(in[0] & 0b0010)>>1 ^(in[1] & 0b0100)>>2^(in[1] & 0b0001)^(in[2] & 0b0100)>>2^(in[2] & 0b0010)>>1^(in[2] & 0b0001);
            bool c0=(in[0] & 0b0001) ^(in[1] & 0b0010)>>1^(in[2] & 0b1000)>>3^(in[2] & 0b0100)>>2^(in[2] & 0b0010)>>1^(in[2] & 0b0001);

            std::cout<<"Payload length: "<<(int)m_payload_len<<std::endl;
            std::cout<<"CRC presence: "<<(int)m_has_crc<<std::endl;
            std::cout<<"Coding rate: "<<(int)m_cr<<std::endl;

            if(header_chk-((int)(c4<<4)+(c3<<3)+(c2<<2)+(c1<<1)+c0)){
                std::cout<<"Header checksum invalid!"<<std::endl<<std::endl;
                message_port_pub(pmt::intern("err"),pmt::mp(true));
                noutput_items = 0;
            }
            else{
                std::cout<<"Header checksum valid!"<<std::endl<<std::endl;
                #ifdef GRLORA_DEBUG
                std::cout<<"should have "<<(int)header_chk<<std::endl;
                std::cout<<"got: "<<(int)(c4<<4)+(c3<<3)+(c2<<2)+(c1<<1)+c0<<std::endl;
                #endif
                message_port_pub(pmt::intern("CR"),pmt::mp(m_cr));
                message_port_pub(pmt::intern("CRC"),pmt::mp(m_has_crc));
                message_port_pub(pmt::intern("pay_len"),pmt::mp(m_payload_len));
                noutput_items = ninput_items[0]-header_len;

            }
            for(int i=header_len , j=0;i<ninput_items[0];i++,j++){
                out[j]=in[i];
                pay_cnt++;
            }
            is_first=false;

            consume_each (ninput_items[0]);
            return noutput_items;
        }
      }
      else{// no header to decode
         for(int i=0;i<ninput_items[0];i++){
             if(pay_cnt<m_payload_len*2+(m_has_crc?4:0)){//only output usefull value (payload and CRC if any)
                nout++;
                pay_cnt++;
                out[i] = in[i];
             }
         }
         consume_each (ninput_items[0]);
         return nout;
      }
      return 0;
    }
  } /* namespace lora */
} /* namespace gr */
