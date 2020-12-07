#include "gray_enc_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

gray_enc::sptr gray_enc::make() {
  return gnuradio::get_initial_sptr(new gray_enc_impl());
}

/**
 * @brief Construct a new gray enc impl object
 *
 */
gray_enc_impl::gray_enc_impl()
    : gr::sync_block("gray_enc", gr::io_signature::make(1, 1, sizeof(uint32_t)),
                     gr::io_signature::make(1, 1, sizeof(uint32_t))) {}

/**
 * @brief Destroy the gray enc impl object
 *
 */
gray_enc_impl::~gray_enc_impl() {}
/**
 * @brief Main function where the actual computation happens
 *
 * @param noutput_items : number of input items
 * @param input_items  : input item (i.e. output data from the interleaving
 * stage)
 * @param output_items : output data
 * @return int
 */
int gray_enc_impl::work(int noutput_items,
                        gr_vector_const_void_star &input_items,
                        gr_vector_void_star &output_items) {
  const uint32_t *in = (const uint32_t *)input_items[0];
  uint32_t *out = (uint32_t *)output_items[0];
  // do the actual gray mapping
  for (int i = 0; i < noutput_items; i++) {
    out[i] = (in[i] ^ (in[i] >> 1u));
    // #ifdef GRLORA_DEBUG
    // //std::cout<<std::hex<<"0x"<<in[i]<<" --->
    // "<<"0x"<<out[i]<<std::dec<<std::endl; #endif
  }
  return noutput_items;
}
} // namespace lora_sdr
} /* namespace gr */
