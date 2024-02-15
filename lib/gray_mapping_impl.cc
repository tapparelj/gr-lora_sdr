#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <gnuradio/lora_sdr/utilities.h>

#include "gray_mapping_impl.h"

namespace gr {
    namespace lora_sdr {

        gray_mapping::sptr
        gray_mapping::make(bool soft_decoding) {
            return gnuradio::get_initial_sptr(new gray_mapping_impl( soft_decoding));
        }

        /*
         * The private constructor
         */
        gray_mapping_impl::gray_mapping_impl(bool soft_decoding)
            : gr::sync_block("gray_mapping",
                             gr::io_signature::make(1, 1, soft_decoding ? MAX_SF * sizeof(LLR) : sizeof(uint16_t)),
                             gr::io_signature::make(1, 1, soft_decoding ? MAX_SF * sizeof(LLR) : sizeof(uint16_t))),
              m_soft_decoding(soft_decoding) {
            set_tag_propagation_policy(TPP_ONE_TO_ONE);
        }

        /*
         * Our virtual destructor.
         */
        gray_mapping_impl::~gray_mapping_impl() {}

        int gray_mapping_impl::work(int noutput_items,
                                gr_vector_const_void_star &input_items,
                                gr_vector_void_star &output_items) {
            const uint16_t *in1 = (const uint16_t *)input_items[0];
            const LLR *in2 = (const LLR *)input_items[0];
            uint16_t *out1 = (uint16_t *)output_items[0];
            LLR *out2 = (LLR *)output_items[0];

            std::vector<tag_t> tags;
            int nitems_to_process = noutput_items;
            get_tags_in_window(tags, 0, 0, noutput_items, pmt::string_to_symbol("frame_info"));
            if (tags.size())
            {
                if (tags[0].offset != nitems_read(0))
                    nitems_to_process = tags[0].offset - nitems_read(0); // only use symbol until the next frame begin (SF might change)

                else
                {
                    if (tags.size() >= 2)
                        nitems_to_process = tags[1].offset - tags[0].offset;

                    pmt::pmt_t err = pmt::string_to_symbol("error");
                    bool is_header = pmt::to_bool(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("is_header"), err));
                    if (is_header) // new frame beginning
                    {
                        int sf = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("sf"), err));
                        m_sf = sf;
                    }      
                }
            }

            for (int i = 0; i < nitems_to_process; i++) {
                if (m_soft_decoding) {
                    // No gray mapping , it has as been done directly in fft_demod block => block "bypass"
                    memcpy(out2 + i * MAX_SF, in2 + i * MAX_SF, MAX_SF * sizeof(LLR));
                } else {
                    out1[i] = (in1[i] ^ (in1[i] >> 1u));  // Gray Demap
                }

#ifdef GRLORA_DEBUG
                std::cout << std::hex << "0x" << in[i] << " ---> "
                          << "0x" << out[i] << std::dec << std::endl; 
#endif
            }
            return nitems_to_process;

        }
    }  // namespace lora_sdr
} /* namespace gr */
