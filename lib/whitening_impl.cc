

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "whitening_impl.h"
#include "tables.h"

namespace gr
{
    namespace lora_sdr
    {

        whitening::sptr
        whitening::make(bool is_hex, bool use_length_tag, char separator, std::string length_tag_name)
        {
            return gnuradio::get_initial_sptr(new whitening_impl(is_hex, use_length_tag, separator, length_tag_name));
        }

        /*
         * The private constructor
         */
        whitening_impl::whitening_impl(bool is_hex, bool use_length_tag, char separator, std::string length_tag_name)
            : gr::sync_interpolator("whitening",
                                    gr::io_signature::make(0, 1, sizeof(uint8_t)),
                                    gr::io_signature::make(1, 1, sizeof(uint8_t)), is_hex ? 1 : 2)
        {
            m_separator = separator;
            m_file_source = false;
            m_use_length_tag = use_length_tag;
            m_length_tag_name = length_tag_name;
            m_is_hex = use_length_tag?false:is_hex;// cant use length tag if input is given as a string of hex values
            m_tag_offset = 1;

            message_port_register_in(pmt::mp("msg"));
            set_msg_handler(pmt::mp("msg"), [this](pmt::pmt_t msg)
                            { this->msg_handler(msg); });
        }

        /*
         * Our virtual destructor.
         */
        whitening_impl::~whitening_impl() {}

        void whitening_impl::msg_handler(pmt::pmt_t message)
        {
            if (m_file_source)
            {
                std::cout << RED << "Whitening can't have both input used simultaneously" << RESET << std::endl;
            }
            //  payload_str.push_back(random_string(rand()%253+2));
            // payload_str.push_back(rand()%2?"12345":"abcdefghijklmnop");
            payload_str.push_back(pmt::symbol_to_string(message));
            // std::copy(payload_str.begin(), payload_str.end(), std::back_inserter(m_payload));
        }

        int whitening_impl::work(int noutput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items)
        {
            // check if input file is used
            uint8_t *in;
            if (input_items.size())
            {
                m_file_source = true;
                in = (uint8_t *)input_items[0];
                std::string s;

                int nitem_to_process = noutput_items;
                int m_frame_len;
                if (m_use_length_tag)
                {
                    // search for tag
                    std::vector<tag_t> tags;
                    get_tags_in_window(tags, 0, 0, noutput_items, pmt::string_to_symbol(m_length_tag_name));
                    if (tags.size())
                    {
                        // process only until next tag
                        if (tags[0].offset != nitems_read(0))
                        {
                            nitem_to_process = tags[0].offset - nitems_read(0);
                        }
                        else // new frame
                        {
                            //only consider tags with a new offset value
                            if(tags[0].offset != m_tag_offset)
                            {
                                if (tags.size() >= 2)
                                {
                                    nitem_to_process = tags[1].offset - tags[0].offset;
                                }
                                m_frame_len = pmt::to_long(tags[0].value);
                                m_tag_offset = tags[0].offset;
                                m_input_byte_cnt = 0;
                                std::cout << "[whitening_impl.cc] offset "<<tags[0].offset<<" New frame of length " << m_frame_len << std::endl;
                            }
                        }
                    }
                    for (int i = 0; i < nitem_to_process; i++) // read payload
                    {
                        s.push_back(in[i]);
                        m_input_byte_cnt++;
                        if (m_input_byte_cnt == m_frame_len)
                        {
                            payload_str.push_back(s);
                        }
                    }
                }

                else
                {
                    for (int i = 0; i < noutput_items / (m_is_hex ? 1 : 2); i++) // read payload
                    {

                        if (in[i] == m_separator)
                        {
                            consume_each(sizeof(m_separator)); // consume the m_separator character
                            payload_str.push_back(s);
                            break;
                        }
                        s.push_back(in[i]);
                    }
                }
            }

            // check if too many messages queued by the message strobe source
            if (payload_str.size() >= 100 && !(payload_str.size() % 100) && !m_file_source)
            {
                std::cout << RED << payload_str.size() << " frames in waiting list. Transmitter has issue to keep up at that transmission frequency." << RESET << std::endl;
            }
            if (payload_str.size() && (uint32_t)noutput_items >= (m_is_hex ? 1 : 2) * payload_str.front().length())
            {
                uint8_t *out = (uint8_t *)output_items[0];
                if (m_is_hex)
                {
                    int len = payload_str.front().length();
                    std::string newString;
                    for (int i = 0; i < len; i += 2)
                    {
                        std::string byte = payload_str.front().substr(i, 2);
                        char chr = (char)(int)strtol(byte.c_str(), NULL, 16);
                        newString.push_back(chr);
                    }
                    payload_str.front() = newString;
                }
                pmt::pmt_t frame_len = pmt::from_long(2 * payload_str.front().length());
                add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_len"), frame_len);

                add_item_tag(0, nitems_written(0), pmt::string_to_symbol("payload_str"), pmt::string_to_symbol(payload_str.front()));

                std::copy(payload_str.front().begin(), payload_str.front().end(), std::back_inserter(m_payload));

                for (unsigned int i = 0; i < m_payload.size(); i++)
                {
                    out[2 * i] = (m_payload[i] ^ whitening_seq[i]) & 0x0F;
                    out[2 * i + 1] = (m_payload[i] ^ whitening_seq[i]) >> 4;
                }
                noutput_items = 2 * m_payload.size();
                m_payload.clear();
                payload_str.erase(payload_str.begin());
            }
            else
                noutput_items = 0;
            return noutput_items;
        }

    } /* namespace lora */
} /* namespace gr */
