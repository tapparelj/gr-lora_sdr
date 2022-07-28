#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "header_impl.h"

namespace gr
{
    namespace lora_sdr
    {

        header::sptr
        header::make(bool impl_head, bool has_crc, uint8_t cr)
        {
            return gnuradio::get_initial_sptr(new header_impl(impl_head, has_crc, cr));
        }

        /*
     * The private constructor
     */
        header_impl::header_impl(bool impl_head, bool has_crc, uint8_t cr)
            : gr::block("header",
                        gr::io_signature::make(1, 1, sizeof(uint8_t)),
                        gr::io_signature::make(1, 1, sizeof(uint8_t)))
        {
            m_cr = cr;
            m_has_crc = has_crc;
            m_impl_head = impl_head;

            m_header.resize(5);

            set_tag_propagation_policy(TPP_DONT);
            m_tags.resize(2);
            m_cnt_header_nibbles = 0;
        }

        void header_impl::set_cr(uint8_t cr){
            m_cr = cr;
        }

        uint8_t header_impl::get_cr(){
            return m_cr;
        }

        /*
     * Our virtual destructor.
     */
        header_impl::~header_impl()
        {
        }

        void
        header_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
        {
            ninput_items_required[0] = 1;
        }

        int
        header_impl::general_work(int noutput_items,
                                  gr_vector_int &ninput_items,
                                  gr_vector_const_void_star &input_items,
                                  gr_vector_void_star &output_items)
        {
            const uint8_t *in = (const uint8_t *)input_items[0];
            uint8_t *out = (uint8_t *)output_items[0];
            int nitems_to_process = std::min(ninput_items[0], noutput_items);
            int out_offset = 0;

            // read tags
            std::vector<tag_t> tags;
            get_tags_in_window(tags, 0, 0, ninput_items[0], pmt::string_to_symbol("frame_len"));
            if (tags.size())
            {
                if (tags[0].offset != nitems_read(0))
                    nitems_to_process = std::min(tags[0].offset - nitems_read(0), (uint64_t)noutput_items);
                else
                {
                    if (tags.size() >= 2)
                        nitems_to_process = std::min(tags[1].offset - tags[0].offset, (uint64_t)noutput_items);

                    m_payload_len = int(pmt::to_long(tags[0].value) / 2);
                    //pass tags downstream
                    tags[0].offset = nitems_written(0);
                    tags[0].value = pmt::from_long(m_payload_len * 2 + (m_impl_head ? 0 : 5)); // 5 being the explicit header length
                    m_tags[0] = tags[0];

                    get_tags_in_window(tags, 0, 0, 1, pmt::string_to_symbol("payload_str"));
                    tags[0].offset = nitems_written(0);
                    m_cnt_nibbles = 0;

                    m_tags[1] = tags[0];
                }
            }

           
            if (m_cnt_nibbles == 0 && !m_impl_head)
            {

                if (m_cnt_header_nibbles == 0)
                {
                    //create header
                    //payload length
                    m_header[0] = (m_payload_len >> 4);
                    m_header[1] = (m_payload_len & 0x0F);

                    //coding rate and has_crc
                    m_header[2] = ((m_cr << 1) | m_has_crc);

                    //header checksum
                    bool c4 = (m_header[0] & 0b1000) >> 3 ^ (m_header[0] & 0b0100) >> 2 ^ (m_header[0] & 0b0010) >> 1 ^ (m_header[0] & 0b0001);
                    bool c3 = (m_header[0] & 0b1000) >> 3 ^ (m_header[1] & 0b1000) >> 3 ^ (m_header[1] & 0b0100) >> 2 ^ (m_header[1] & 0b0010) >> 1 ^ (m_header[2] & 0b0001);
                    bool c2 = (m_header[0] & 0b0100) >> 2 ^ (m_header[1] & 0b1000) >> 3 ^ (m_header[1] & 0b0001) ^ (m_header[2] & 0b1000) >> 3 ^ (m_header[2] & 0b0010) >> 1;
                    bool c1 = (m_header[0] & 0b0010) >> 1 ^ (m_header[1] & 0b0100) >> 2 ^ (m_header[1] & 0b0001) ^ (m_header[2] & 0b0100) >> 2 ^ (m_header[2] & 0b0010) >> 1 ^ (m_header[2] & 0b0001);
                    bool c0 = (m_header[0] & 0b0001) ^ (m_header[1] & 0b0010) >> 1 ^ (m_header[2] & 0b1000) >> 3 ^ (m_header[2] & 0b0100) >> 2 ^ (m_header[2] & 0b0010) >> 1 ^ (m_header[2] & 0b0001);

                    m_header[3] = c4;
                    m_header[4] = c3 << 3 | c2 << 2 | c1 << 1 | c0;

                    //add tag
                    add_item_tag(0, m_tags[0]);
                    add_item_tag(0, m_tags[1]);
                }

                for (int i = 0; i < nitems_to_process; i++)
                {
                    if (m_cnt_header_nibbles < 5)
                    {
                        out[i] = m_header[m_cnt_header_nibbles];
                        m_cnt_header_nibbles++;
                        out_offset++;
                    }
                    else
                    {
                        break;
                    }
                    
                }
            }
            if (m_impl_head && m_cnt_nibbles == 0)
            {
                add_item_tag(0, m_tags[0]);
                add_item_tag(0, m_tags[1]);
            }
            for (int i = out_offset; i < nitems_to_process; i++)
            {
                out[i] = in[i - out_offset];
                m_cnt_nibbles++;
                m_cnt_header_nibbles = 0;
            }

          
            consume_each(nitems_to_process - out_offset);
            return nitems_to_process;
        }

    } /* namespace lora */
} /* namespace gr */
