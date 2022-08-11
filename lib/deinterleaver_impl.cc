#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <gnuradio/lora_sdr/utilities.h>

#include "deinterleaver_impl.h"

namespace gr {
    namespace lora_sdr {

        deinterleaver::sptr
        deinterleaver::make(bool soft_decoding) {
            return gnuradio::get_initial_sptr(new deinterleaver_impl( soft_decoding));
        }

        /*
         * The private constructor
         */
        deinterleaver_impl::deinterleaver_impl( bool soft_decoding)
            : gr::block("deinterleaver",
                        gr::io_signature::make(1, 1, soft_decoding ? MAX_SF * sizeof(LLR) : sizeof(uint16_t)),  // In reality: sf_app               < sf
                        gr::io_signature::make(1, 1, soft_decoding ? 8 * sizeof(LLR) : sizeof(uint8_t))),   // In reality: cw_len = cr_app + 4  < 8
              m_soft_decoding(soft_decoding)
               {
            set_tag_propagation_policy(TPP_DONT);
        }

        /*
         * Our virtual destructor.
         */
        deinterleaver_impl::~deinterleaver_impl() {}

        void deinterleaver_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required) {
            ninput_items_required[0] = 4;
        }

        int deinterleaver_impl::general_work(int noutput_items,
                                             gr_vector_int &ninput_items,
                                             gr_vector_const_void_star &input_items,
                                             gr_vector_void_star &output_items) {
            const uint16_t *in1 = (const uint16_t *)input_items[0];
            const LLR *in2 = (const LLR *)input_items[0];
            uint8_t *out1 = (uint8_t *)output_items[0];
            LLR *out2 = (LLR *)output_items[0];

            std::vector<tag_t> tags;
            get_tags_in_window(tags, 0, 0, 1, pmt::string_to_symbol("frame_info"));
            if (tags.size()) {
                pmt::pmt_t err = pmt::string_to_symbol("error");
                m_is_header = pmt::to_bool(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("is_header"), err));
                
                if (m_is_header) {
                    m_sf = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("sf"), err));
                    // std::cout<<"deinterleaver_header "<<tags[0].offset<<std::endl;
                    // is_first = true;
                } else {
                    // is_first=false;
                    m_cr = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cr"), err));
                    m_ldro = pmt::to_bool(pmt::dict_ref(tags[0].value,pmt::string_to_symbol("ldro"),err));
                    // std::cout<<"\ndeinter_cr "<<tags[0].offset<<" - cr: "<<(int)m_cr<<"\n";
                }
                tags[0].offset = nitems_written(0);
                add_item_tag(0, tags[0]);

            }
            sf_app = (m_is_header||m_ldro) ? m_sf - 2 : m_sf;  // Use reduced rate for the first block
            cw_len = m_is_header ? 8 : m_cr + 4;
            // std::cout << "sf_app " << +sf_app << " cw_len " << +cw_len << std::endl;

            if (ninput_items[0] >= cw_len) {  // wait for a full block to deinterleave

                if (m_soft_decoding) {
                    // Create the empty matrices
                    std::vector<LLR> init_LLR1(sf_app, 0);
                    std::vector<std::vector<LLR>> inter_bin(cw_len, init_LLR1);
                    std::vector<LLR> init_LLR2(cw_len, 0);
                    std::vector<std::vector<LLR>> deinter_bin(sf_app, init_LLR2);

                    for (uint32_t i = 0; i < cw_len; i++) {
                        // take only sf_app bits over the sf bits available
                        memcpy(inter_bin[i].data(), in2 + (i * m_sf + m_sf - sf_app), sf_app * sizeof(LLR));
                    }

                    // Do the actual deinterleaving
                    for (int32_t i = 0; i < cw_len; i++) {
                        for (int32_t j = 0; j < int(sf_app); j++) {
                            // std::cout << "T["<<i<<"]["<<j<<"] "<< (inter_bin[i][j] > 0) << " ";
                            deinter_bin[mod((i - j - 1), sf_app)][i] = inter_bin[i][j];
                        }
                        // std::cout << std::endl;
                    }

                    for (uint32_t i = 0; i < sf_app; i++) {
                        // Write only the cw_len bits over the 8 bits space available
                        memcpy(out2 + i * 8, deinter_bin[i].data(), cw_len * sizeof(LLR));
                    }

                } 
                else {  // Hard-Decoding
                    // Create the empty matrices
                    std::vector<std::vector<bool>> inter_bin(cw_len);
                    std::vector<bool> init_bit(cw_len, 0);
                    std::vector<std::vector<bool>> deinter_bin(sf_app, init_bit);

                    // convert decimal vector to binary vector of vector
                    for (int i = 0; i < cw_len; i++) {
                        inter_bin[i] = int2bool(in1[i], sf_app);
                    }
#ifdef GRLORA_DEBUG
                    std::cout << "interleaved----" << std::endl;
                    for (uint32_t i = 0u; i < cw_len; i++) {
                        for (int j = 0; j < int(sf_app); j++) {
                            std::cout << inter_bin[i][j];
                        }
                        std::cout << " " << (int)in1[i] << std::endl;
                    }
                    std::cout << std::endl;
#endif
                    // Do the actual deinterleaving
                    for (int32_t i = 0; i < cw_len; i++) {
                        for (int32_t j = 0; j < int(sf_app); j++) {
                            // std::cout << "T["<<i<<"]["<<j<<"] "<< inter_bin[i][j] << " ";
                            deinter_bin[mod((i - j - 1), sf_app)][i] = inter_bin[i][j];
                        }
                        // std::cout << std::endl;
                    }

                    // transform codewords from binary vector to dec
                    for (uint i = 0; i < sf_app; i++) {
                        out1[i] = bool2int(deinter_bin[i]);  // bool2int return uint32_t Maybe explicit conversion to uint8_t
                    }

#ifdef GRLORA_DEBUG
                    std::cout << "codewords----" << std::endl;
                    for (uint32_t i = 0u; i < sf_app; i++) {
                        for (int j = 0; j < int(cw_len); j++) {
                            std::cout << deinter_bin[i][j];
                        }
                        std::cout << " 0x" << std::hex << (int)out1[i] << std::dec << std::endl;
                    }
                    std::cout << std::endl;
#endif
                    // if(is_first)
                    //     add_item_tag(0, nitems_written(0), pmt::string_to_symbol("header_len"), pmt::mp((long)sf_app));//sf_app is the header part size

                    // consume_each(cw_len);
                }
                consume_each(cw_len);

                if (noutput_items < sf_app)
                    std::cout << RED << "[deinterleaver.cc] Not enough output space! " << noutput_items << "/" << sf_app << std::endl;

                return sf_app;
            }
            return 0;
        }
    }  // namespace lora_sdr
} /* namespace gr */
