#include "hamming_enc_impl.h"
#include <gnuradio/io_signature.h>
#include <lora_sdr/utilities.h>

namespace gr {
namespace lora_sdr {

hamming_enc::sptr hamming_enc::make(uint8_t cr, uint8_t sf) {
  return gnuradio::get_initial_sptr(new hamming_enc_impl(cr, sf));
}

/**
 * @brief Construct a new hamming enc impl object
 *
 * @param cr : coding rate
 * @param sf : spreading factor
 */
hamming_enc_impl::hamming_enc_impl(uint8_t cr, uint8_t sf)
    : gr::sync_block("hamming_enc",
                     gr::io_signature::make(1, 1, sizeof(uint8_t)),
                     gr::io_signature::make(1, 1, sizeof(uint8_t))) {
  m_cr = cr;
  m_sf = sf;
}

/**
 * @brief Destroy the hamming enc impl object
 *
 */
hamming_enc_impl::~hamming_enc_impl() {}

/**
 * @brief Main function that does the actual hamming encoding.
 * With cr : coding rate, and sf : spreading factor
 *
 * @param noutput_items : number of output items
 * @param input_items : number of input items
 * @param output_items : number of output items
 * @return int
 */
int hamming_enc_impl::work(int noutput_items,
                           gr_vector_const_void_star &input_items,
                           gr_vector_void_star &output_items) {
  const uint8_t *in_data = (const uint8_t *)input_items[0];
  uint8_t *out = (uint8_t *)output_items[0];
  
  std::vector<bool> data_bin;
  bool p0, p1, p2, p3, p4;
  //loop over the input items to do the actual hamming encoding
  for (int i = 0; i < noutput_items; i++) {
// #ifdef GRLORA_DEBUG
// // std::cout<<std::hex<<(int)in_data[i]<<"   ";
// #endif
    uint8_t cr_app = (i < m_sf - 2) ? 4 : m_cr;
    data_bin = int2bool(in_data[i], 4);

    // the data_bin is msb first
    if (cr_app != 1) { // need hamming parity bits
      p0 = data_bin[3] ^ data_bin[2] ^ data_bin[1];
      p1 = data_bin[2] ^ data_bin[1] ^ data_bin[0];
      p2 = data_bin[3] ^ data_bin[2] ^ data_bin[0];
      p3 = data_bin[3] ^ data_bin[1] ^ data_bin[0];
      // we put the data LSB first and append the parity bits
      out[i] = (data_bin[3] << 7 | data_bin[2] << 6 | data_bin[1] << 5 |
                data_bin[0] << 4 | p0 << 3 | p1 << 2 | p2 << 1 | p3) >>
               (4 - cr_app);

    } else { // coding rate = 4/5 we add a parity bit
      p4 = data_bin[0] ^ data_bin[1] ^ data_bin[2] ^ data_bin[3];
      out[i] = (data_bin[3] << 4 | data_bin[2] << 3 | data_bin[1] << 2 |
                data_bin[0] << 1 | p4);
    }
// #ifdef GRLORA_DEBUG
//     // std::cout<<std::hex<<(int)out[i]<<std::dec<<std::endl;
// #endif
  }

  return noutput_items;
}

} // namespace lora_sdr
} /* namespace gr */
