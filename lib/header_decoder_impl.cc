
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "header_decoder_impl.h"
#include <gnuradio/lora_sdr/utilities.h>

namespace gr
{
    namespace lora_sdr
    {

        header_decoder::sptr
        header_decoder::make(bool impl_head, uint8_t cr, uint32_t pay_len, bool has_crc, uint8_t ldro_mode, bool print_header)
        {
            return gnuradio::get_initial_sptr(new header_decoder_impl(impl_head, cr, pay_len, has_crc, ldro_mode, print_header));
        }

        /*
     * The private constructor
     */
        header_decoder_impl::header_decoder_impl(bool impl_head, uint8_t cr, uint32_t pay_len, bool has_crc, uint8_t ldro_mode, bool print_header)
            : gr::block("header_decoder",
                        gr::io_signature::make(1, 1, sizeof(uint8_t)),
                        gr::io_signature::make(1, 1, sizeof(uint8_t)))
        {
            m_impl_header = impl_head;
            m_print_header = print_header;
            m_cr = cr;
            m_payload_len = pay_len;
            m_has_crc = has_crc;
            m_ldro_mode = ldro_mode;

            pay_cnt = 0;

            set_tag_propagation_policy(TPP_DONT);
            message_port_register_out(pmt::mp("frame_info"));


        }
        /*
     * Our virtual destructor.
     */
        header_decoder_impl::~header_decoder_impl()
        {
        }

        void
        header_decoder_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
        {
            ninput_items_required[0] = noutput_items;
        }

        void header_decoder_impl::publish_frame_info(int cr, int pay_len, int crc, uint8_t ldro_mode, int err)
        {

            pmt::pmt_t header_content = pmt::make_dict();

            header_content = pmt::dict_add(header_content, pmt::intern("cr"), pmt::from_long(cr));
            header_content = pmt::dict_add(header_content, pmt::intern("pay_len"), pmt::from_long(pay_len));
            header_content = pmt::dict_add(header_content, pmt::intern("crc"), pmt::from_long(crc));
            header_content = pmt::dict_add(header_content, pmt::intern("ldro_mode"), pmt::from_long(ldro_mode));
            header_content = pmt::dict_add(header_content, pmt::intern("err"), pmt::from_long(err));
            message_port_pub(pmt::intern("frame_info"), header_content);
            if(!err) //don't propagate downstream that a frame was detected
                add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_info"), header_content);
        }

        int header_decoder_impl::general_work(int noutput_items,
                                              gr_vector_int &ninput_items,
                                              gr_vector_const_void_star &input_items,
                                              gr_vector_void_star &output_items)
        {
            const uint8_t *in = (const uint8_t *)input_items[0];
            uint8_t *out = (uint8_t *)output_items[0];
           
            int nitem_to_process = ninput_items[0];

            std::vector<tag_t> tags;
            get_tags_in_window(tags, 0, 0, ninput_items[0], pmt::string_to_symbol("frame_info"));
            if (tags.size())
            {
                if (tags[0].offset != nitems_read(0))
                {
                    nitem_to_process = tags[0].offset - nitems_read(0);
                }
                else
                {
                    if (tags.size() >= 2)
                    {
                        nitem_to_process = tags[1].offset - tags[0].offset;
                    }
                    else
                    {
                        nitem_to_process = ninput_items[0];
                    }
                    pmt::pmt_t err = pmt::string_to_symbol("error");
                    is_header = pmt::to_bool(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("is_header"), err));
                    // print("ac ishead: "<<is_header);
                    if (is_header)
                    {
                        pay_cnt = 0;
                    }
                }
            }
            if (is_header && nitem_to_process < 5 && !m_impl_header) //ensure to have a full PHY header to process
            {
                nitem_to_process = 0;
            }
            if (is_header)
            {
                if (m_impl_header)
                { //implicit header, all parameters should have been provided
                    publish_frame_info(m_cr, m_payload_len, m_has_crc, m_ldro_mode, 0);

                    for (int i = 0; i < nitem_to_process; i++)
                    {
                        //only output payload or CRC
                        if (pay_cnt < (uint32_t)m_payload_len * 2 + (m_has_crc ? 4 : 0))
                        {
                            out[i] = in[i];
                            pay_cnt++;
                        }
                    }
                    consume_each(nitem_to_process);
                    return pay_cnt;
                }
                else
                { //explicit header to decode
                    
                    m_payload_len = (in[0] << 4) + in[1];
                    
                    m_has_crc = in[2] & 1;
                    m_cr = in[2] >> 1;

                    header_chk = ((in[3] & 1) << 4) + in[4];

                    //check header Checksum
                    bool c4 = (in[0] & 0b1000) >> 3 ^ (in[0] & 0b0100) >> 2 ^ (in[0] & 0b0010) >> 1 ^ (in[0] & 0b0001);
                    bool c3 = (in[0] & 0b1000) >> 3 ^ (in[1] & 0b1000) >> 3 ^ (in[1] & 0b0100) >> 2 ^ (in[1] & 0b0010) >> 1 ^ (in[2] & 0b0001);
                    bool c2 = (in[0] & 0b0100) >> 2 ^ (in[1] & 0b1000) >> 3 ^ (in[1] & 0b0001) ^ (in[2] & 0b1000) >> 3 ^ (in[2] & 0b0010) >> 1;
                    bool c1 = (in[0] & 0b0010) >> 1 ^ (in[1] & 0b0100) >> 2 ^ (in[1] & 0b0001) ^ (in[2] & 0b0100) >> 2 ^ (in[2] & 0b0010) >> 1 ^ (in[2] & 0b0001);
                    bool c0 = (in[0] & 0b0001) ^ (in[1] & 0b0010) >> 1 ^ (in[2] & 0b1000) >> 3 ^ (in[2] & 0b0100) >> 2 ^ (in[2] & 0b0010) >> 1 ^ (in[2] & 0b0001);
                    if(m_print_header){
                        std::cout << "\n--------Header--------" << std::endl;
                        std::cout << "Payload length: " << (int)m_payload_len << std::endl;
                        std::cout << "CRC presence:   " << (int)m_has_crc << std::endl;
                        std::cout << "Coding rate:    " << (int)m_cr << std::endl;
                    }
                    int head_err = header_chk - ((int)(c4 << 4) + (c3 << 3) + (c2 << 2) + (c1 << 1) + c0);
                    if (head_err||m_payload_len==0)
                    {
                        if(m_print_header && head_err)
                            std::cout <<RED<< "Header checksum invalid!" <<RESET<< std::endl<< std::endl;
                        if(m_print_header && m_payload_len==0)
                            std::cout <<RED<< "Frame can not be empty!" <<RESET<<"item to process= "<<nitem_to_process<< std::endl<< std::endl;
                        // message_port_pub(pmt::intern("err"),pmt::mp(true));
                        head_err = 1;
                        noutput_items = 0;
                    }
                    else
                    {
                        if(m_print_header) std::cout << "Header checksum valid!" << std::endl<< std::endl;
#ifdef GRLORA_DEBUG
                        std::cout << "should have " << (int)header_chk << std::endl;
                        std::cout << "got: " << (int)(c4 << 4) + (c3 << 3) + (c2 << 2) + (c1 << 1) + c0 << std::endl;
#endif
                        noutput_items = nitem_to_process - header_len;
                    }
                    publish_frame_info(m_cr, m_payload_len, m_has_crc, m_ldro_mode, head_err);
                    // print("pub header info");
                    for (int i = header_len, j = 0; i < nitem_to_process; i++, j++)
                    {
                        out[j] = in[i];
                        pay_cnt++;
                    }
                    consume_each(nitem_to_process);
                    return noutput_items;
                }
            }
            else
            { // no header to decode
                nout = 0;
                for (int i = 0; i < nitem_to_process; i++)
                {
                    if (pay_cnt < (uint32_t)m_payload_len * 2 + (m_has_crc ? 4 : 0))
                    { //only output usefull value (payload and CRC if any)
                        nout++;
                        pay_cnt++;
                        out[i] = in[i];
                    }
                }
                consume_each(nitem_to_process);
                return nout;
            }
            return 0;
        }
    } /* namespace lora */
} /* namespace gr */
