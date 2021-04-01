

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
        whitening::make()
        {
            return gnuradio::get_initial_sptr(new whitening_impl());
        }

        /*
     * The private constructor
     */
        whitening_impl::whitening_impl()
            : gr::sync_block("whitening",
                             gr::io_signature::make(0, 0, 0),
                             gr::io_signature::make(0, 1, sizeof(uint8_t)))
        {
            new_message = false;

            message_port_register_in(pmt::mp("msg"));
            set_msg_handler(pmt::mp("msg"), [this](pmt::pmt_t msg) { this->msg_handler(msg); });
        }

        /*
     * Our virtual destructor.
     */
        whitening_impl::~whitening_impl()
        {
        }
        
        void whitening_impl::msg_handler(pmt::pmt_t message)
        {

            //  payload_str.push_back(random_string(rand()%253+2));
            // payload_str.push_back(rand()%2?"12345":"abcdefghijklmnop");
            payload_str.push_back(pmt::symbol_to_string(message));            
            // std::copy(payload_str.begin(), payload_str.end(), std::back_inserter(m_payload));
            new_message = true;
        }

        int whitening_impl::work(int noutput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items)
        {
            if (payload_str.size()>=100 && !(payload_str.size()%100))
                std::cout<<RED<<payload_str.size()<<" frames in waiting list. Transmitter has issue to keep up at that transmission frequency."<<RESET<<std::endl;
            if (payload_str.size() && noutput_items >= 2*payload_str.front().length())
            {
                pmt::pmt_t frame_len = pmt::from_long(2*payload_str.front().length());
                add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_len"), frame_len);

                add_item_tag(0, nitems_written(0), pmt::string_to_symbol("payload_str"), pmt::string_to_symbol(payload_str.front()));

                uint8_t *out = (uint8_t *)output_items[0];

                std::copy(payload_str.front().begin(), payload_str.front().end(), std::back_inserter(m_payload));;

                for (uint i = 0; i < m_payload.size(); i++)
                {
                    out[2 * i] = (m_payload[i] ^ whitening_seq[i]) & 0x0F;
                    out[2 * i + 1] = (m_payload[i] ^ whitening_seq[i]) >> 4;
                }

                noutput_items = 2 * m_payload.size();
                m_payload.clear();
                payload_str.erase(payload_str.begin());
                new_message = false;
            }
            else
                noutput_items = 0;
            return noutput_items;
        }

    } /* namespace lora */
} /* namespace gr */
