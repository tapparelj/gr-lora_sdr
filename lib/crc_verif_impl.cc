#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <chrono>
#include "crc_verif_impl.h"

#include <gnuradio/lora_sdr/utilities.h> // for print color

namespace gr
{
    namespace lora_sdr
    {

        crc_verif::sptr
        crc_verif::make(bool print_rx_msg, bool output_crc_check)
        {
            return gnuradio::get_initial_sptr(new crc_verif_impl(print_rx_msg, output_crc_check));
        }

        /*
         * The private constructor
         */
        crc_verif_impl::crc_verif_impl(bool print_rx_msg, bool output_crc_check)
            : gr::block("crc_verif",
                        gr::io_signature::make(1, 1, sizeof(uint8_t)),
                        gr::io_signature::make2(0, 2, sizeof(uint8_t), sizeof(uint8_t))),
              print_rx_msg(print_rx_msg),
                  output_crc_check(output_crc_check)
        {
            message_port_register_out(pmt::mp("msg"));
        }

        /*
         * Our virtual destructor.
         */
        crc_verif_impl::~crc_verif_impl()
        {
        }

        void crc_verif_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
        {
            ninput_items_required[0] = 1; // m_payload_len;
        }
        unsigned int crc_verif_impl::crc16(uint8_t *data, uint32_t len)
        {

            uint16_t crc = 0x0000;
            for (uint i = 0; i < len; i++)
            {
                uint8_t newByte = data[i];

                for (unsigned char i = 0; i < 8; i++)
                {
                    if (((crc & 0x8000) >> 8) ^ (newByte & 0x80))
                    {
                        crc = (crc << 1) ^ 0x1021;
                    }
                    else
                    {
                        crc = (crc << 1);
                    }
                    newByte <<= 1;
                }
            }
            return crc;
        }

        int crc_verif_impl::general_work(int noutput_items,
                                         gr_vector_int &ninput_items,
                                         gr_vector_const_void_star &input_items,
                                         gr_vector_void_star &output_items)
        {
            uint8_t *in = (uint8_t *)input_items[0];
            uint8_t *out;
            bool *out_crc;
            if (output_items.size())
            {
                out = (uint8_t *)output_items[0];
                if (output_crc_check)
                    out_crc = (bool *)output_items[1]; 
            }

            std::vector<tag_t> tags;
            get_tags_in_window(tags, 0, 0, ninput_items[0], pmt::string_to_symbol("frame_info"));
            if (tags.size())
            {
                pmt::pmt_t err = pmt::string_to_symbol("error");
                m_crc_presence = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("crc"), err));
                m_payload_len = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("pay_len"), err));
                // std::cout<<m_payload_len<<" "<<nitem_to_process<<std::endl;
                // std::cout<<"\ncrc_crc "<<tags[0].offset<<" - crc: "<<(int)m_crc_presence<<" - pay_len: "<<(int)m_payload_len<<"\n";
                
                
            }
            //append received bytes to buffer
            for (int i = 0; i < ninput_items[0]; i++)
            {
                in_buff.push_back(in[i]);
            }
            consume_each(ninput_items[0]);
            

            if ((in_buff.size() >= (int)m_payload_len + 2) && m_crc_presence)
            { // wait for all the payload to come
                
                if (m_payload_len < 2)
                { // undefined CRC
                    std::cout << "CRC not supported for payload smaller than 2 bytes" << std::endl;
                    return 0;
                }
                else
                {
                    // calculate CRC on the N-2 firsts data bytes
                    m_crc = crc16(&in_buff[0], m_payload_len - 2);

                    // XOR the obtained CRC with the last 2 data bytes
                    m_crc = m_crc ^ in_buff[m_payload_len - 1] ^ (in_buff[m_payload_len - 2] << 8);
#ifdef GRLORA_DEBUG
                    for (int i = 0; i < (int)m_payload_len + 2; i++)
                        std::cout << std::hex << (int)in_buff[i] << std::dec << std::endl;
                    std::cout << "Calculated " << std::hex << m_crc << std::dec << std::endl;
                    std::cout << "Got " << std::hex << (in_buff[m_payload_len] + (in_buff[m_payload_len + 1] << 8)) << std::dec << std::endl;
#endif

                    // get payload as string
                    message_str.clear();
                    for (int i = 0; i < (int)m_payload_len; i++)
                    {
                        m_char = (char)in_buff[i];
                        message_str = message_str + m_char;
                        if (output_items.size())
                            out[i] = in_buff[i];
                    }
                    cnt++;
                    uint8_t crc_valid;
                    if (!(in_buff[m_payload_len] + (in_buff[m_payload_len + 1] << 8) - m_crc))
                        crc_valid = 1;
                    else
                        crc_valid = 0;
                    
                    if(output_crc_check){
                        out_crc[0] = crc_valid;
                        produce(1,1);
                    }

                    if (print_rx_msg)
                    {
                        std::cout << "rx msg: " << message_str << std::endl
                                  << std::endl;

                        if (crc_valid)
                            std::cout << "CRC valid!" << std::endl
                                      << std::endl;
                        else
                            std::cout << RED << "CRC invalid" << RESET << std::endl
                                      << std::endl;
                    }
                    message_port_pub(pmt::intern("msg"), pmt::mp(message_str));
                    in_buff.erase(in_buff.begin(), in_buff.begin()+m_payload_len + 2);
                    if(output_crc_check){
                        produce(0,m_payload_len);
                        return WORK_CALLED_PRODUCE;
                    }
                    else
                        return m_payload_len;
                }
            }
            else if ((in_buff.size()>= (int)m_payload_len) && !m_crc_presence)
            {
                
                // get payload as string
                message_str.clear();
                for (uint i = 0; i < m_payload_len; i++)
                {
                    m_char = (char)in_buff[i];
                    message_str = message_str + m_char;
                    if (output_items.size())
                        out[i] = in_buff[i];
                }
                cnt++;
                in_buff.erase(in_buff.begin(), in_buff.begin() + m_payload_len );
                if (print_rx_msg)
                    std::cout << "rx msg: " << message_str << std::endl;
                message_port_pub(pmt::intern("msg"), pmt::mp(message_str));
                
                return m_payload_len;
            }
            else
                return 0;
            
        }
    } /* namespace lora */
} /* namespace gr */
