#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <gnuradio/lora_sdr/utilities.h>

#include "gray_mapping_impl.h"

namespace gr {
    namespace lora_sdr {

        gray_mapping::sptr
        gray_mapping::make(uint8_t sf, bool soft_decoding) {
            return gnuradio::get_initial_sptr(new gray_mapping_impl(sf, soft_decoding));
        }

        /*
         * The private constructor
         */
        gray_mapping_impl::gray_mapping_impl(uint8_t sf, bool soft_decoding)
            : gr::sync_block("gray_mapping",
                             gr::io_signature::make(1, 1, soft_decoding ? sf * sizeof(LLR) : sizeof(uint32_t)),
                             gr::io_signature::make(1, 1, soft_decoding ? sf * sizeof(LLR) : sizeof(uint32_t))),
              m_sf(sf),
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
            const uint32_t *in1 = (const uint32_t *)input_items[0];
            const LLR *in2 = (const LLR *)input_items[0];
            uint32_t *out1 = (uint32_t *)output_items[0];
            LLR *out2 = (LLR *)output_items[0];

            for (int i = 0; i < noutput_items; i++) {
                if (m_soft_decoding) {
                    // No gray demapping as already done in fft_demod block => block "bypass"
                    memcpy(out2 + i * m_sf, in2 + i * m_sf, m_sf * sizeof(LLR));
                } else {
                    out1[i] = (in1[i] ^ (in1[i] >> 1u));  // Gray Demap
                }

#ifdef GRLORA_DEBUG
                std::cout << std::hex << "0x" << in[i] << " ---> "
                          << "0x" << out[i] << std::dec << std::endl;  // TODO change in out !!
#endif
            }
            return noutput_items;
        }
    }  // namespace lora_sdr
} /* namespace gr */
