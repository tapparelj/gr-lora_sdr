#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "crc_verif_impl.h"

namespace gr {
  namespace lora_sdr {

    crc_verif::sptr
    crc_verif::make( )
    {
      return gnuradio::get_initial_sptr
        (new crc_verif_impl());
    }

    /*
     * The private constructor
     */
    crc_verif_impl::crc_verif_impl( )
      : gr::block("crc_verif",
              gr::io_signature::make(1, 1, sizeof(uint8_t)),
              gr::io_signature::make(0, 0, 0))
    {
        message_port_register_out(pmt::mp("msg"));

        message_port_register_in(pmt::mp("pay_len"));
        set_msg_handler(pmt::mp("pay_len"), boost::bind(&crc_verif_impl::header_pay_len_handler, this, _1));
        message_port_register_in(pmt::mp("CRC"));
        set_msg_handler(pmt::mp("CRC"), boost::bind(&crc_verif_impl::header_crc_handler, this, _1));

    }

    /*
     * Our virtual destructor.
     */
    crc_verif_impl::~crc_verif_impl()
    {}

    void crc_verif_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required){
        ninput_items_required[0] = 1;//m_payload_len;
    }
    unsigned int crc_verif_impl::crc16(uint8_t* data, uint32_t len) {

        uint16_t crc = 0x0000;
        for(uint i=0;i<len;i++) {
            uint8_t newByte=data[i];

            for (unsigned char i = 0; i < 8; i++) {
                if (((crc & 0x8000) >> 8) ^ (newByte & 0x80)){
                    crc = (crc << 1)  ^ 0x1021;
                }else{
                    crc = (crc << 1);
                }
                newByte <<= 1;
            }
        }
        return crc;
    }

    void crc_verif_impl::header_pay_len_handler(pmt::pmt_t payload_len){
        m_payload_len=pmt::to_long(payload_len);
        in_buff.clear();
    };
    void crc_verif_impl::header_crc_handler(pmt::pmt_t crc_presence){
        m_crc_presence=pmt::to_long(crc_presence);
    };

    int crc_verif_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        uint8_t *in = (uint8_t *) input_items[0];
        bool *out = (bool *) output_items[0];
        // std::cout << "input items: "<< ninput_items[0] << '\n';
        for (size_t i = 0; i < ninput_items[0]; i++) {
            in_buff.push_back(in[i]);
        }
        consume_each (ninput_items[0]);

        if(in_buff.size()>=(int)m_payload_len+2 && m_crc_presence){//wait for all the payload to come
            if(m_payload_len<2)//undefined CRC
                std::cout << "Disable CRC for payload smaller than 2 bytes" << '\n';
            else{
            //calculate CRC on the N-2 firsts data bytes
            m_crc=crc16(&in_buff[0],m_payload_len-2);

            //XOR the obtained CRC with the last 2 data bytes
            m_crc = m_crc ^ in_buff[m_payload_len-1] ^ (in_buff[m_payload_len-2]<<8);
            #ifdef GRLORA_DEBUG
            for(int i =0;i<in_buff.size();i++)
            std::cout<< std::hex << (int)in_buff[i]<<std::dec<<std::endl;
            std::cout<<"Calculated "<<std::hex<<m_crc<<std::dec<<std::endl;
            std::cout<<"Got "<<std::hex<<(in_buff[m_payload_len]+(in_buff[m_payload_len+1]<<8))<<std::dec<<std::endl;
            #endif

            //get payload as string
            message_str.clear();
            for(int i =0;i<in_buff.size()-2;i++){
                m_char= (char)in_buff[i];
                message_str = message_str+m_char;
            }
            std::cout<<"msg: "<<message_str<<std::endl<<std::endl;
            if(!(in_buff[m_payload_len]+(in_buff[m_payload_len+1]<<8)-m_crc))
                std::cout<<"CRC valid!"<<std::endl<<std::endl;
            else
                std::cout<<"CRC invalid"<<std::endl<<std::endl;
            message_port_pub(pmt::intern("msg"),pmt::mp(message_str));
            in_buff.clear();
            return 0;
            }
        }
        else if(in_buff.size()>=(int)m_payload_len && !m_crc_presence){
            //get payload as string
            message_str.clear();
            for(int i =0;i<in_buff.size();i++){
                m_char= (char)in_buff[i];
                message_str=message_str+m_char;
            }
            std::cout<<"msg: "<<message_str<<std::endl;
            message_port_pub(pmt::intern("msg"),pmt::mp(message_str));
            in_buff.clear();
            return 0;
        }
        else
            return 0;
    }
  } /* namespace lora */
} /* namespace gr */
