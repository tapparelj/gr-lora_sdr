#include "gray_decode_impl.h"
#include <gnuradio/io_signature.h>
#include "helpers.h"

namespace gr {
namespace lora_sdr {

gray_decode::sptr gray_decode::make(uint8_t sf) {
  return gnuradio::get_initial_sptr(new gray_decode_impl(sf));
}
/**
 * @brief Construct a new gray decode impl object
 *
 * @param sf : sampling rate
 */
gray_decode_impl::gray_decode_impl(uint8_t sf)
    : gr::sync_block("gray_decode",
                     gr::io_signature::make(1, 1, sizeof(uint32_t)),
                     gr::io_signature::make(1, 1, sizeof(uint32_t))) {
  m_sf = sf;
  set_tag_propagation_policy(TPP_ALL_TO_ALL);
}

/**
 * @brief Destroy the gray decode impl object
 *
 */
gray_decode_impl::~gray_decode_impl() {}

/**
 * @brief Main function where the actual computation resides
 *
 * @param noutput_items : number of output items
 * @param input_items : input items (i.e. fft_demod)
 * @param output_items : output data
 * @return int
 */
int gray_decode_impl::work(int noutput_items,
                           gr_vector_const_void_star &input_items,
                           gr_vector_void_star &output_items) {
  const uint32_t *in = (const uint32_t *)input_items[0];
  uint32_t *out = (uint32_t *)output_items[0];
  std::vector<tag_t> return_tag;
  get_tags_in_range(return_tag, 0, 0, nitems_read(0) + 1);
  if (return_tag.size() > 0) {
    add_item_tag(0, nitems_written(0), pmt::intern("status"),
                 pmt::intern("done"));
                 return 1;
  }

  for (int i = 0; i < noutput_items; i++) {
#ifdef GRLORA_DEBUG
// std::cout<<std::hex<<"0x"<<in[i]<<" -->  ";
#endif
    out[i] = in[i];
    for (int j = 1; j < m_sf; j++) {
      out[i] = out[i] ^ (in[i] >> j);
    }
    // do the shift of 1
    out[i] = mod(out[i] + 1, (1 << m_sf));
#ifdef GRLORA_DEBUG
// std::cout<<"0x"<<out[i]<<std::dec<<std::endl;
#endif
  }

  return noutput_items;
}
} // namespace lora_sdr
} /* namespace gr */
