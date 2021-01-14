
#include "hamming_dec_impl.h"
#include <gnuradio/io_signature.h>
#include <lora_sdr/utilities.h>
//Fix for libboost > 1.75
#include <boost/bind/placeholders.hpp>

using namespace boost::placeholders;

namespace gr {
namespace lora_sdr {

hamming_dec::sptr hamming_dec::make() {
  return gnuradio::get_initial_sptr(new hamming_dec_impl());
}

/**
 * @brief Construct a new hamming dec impl object
 *
 */
hamming_dec_impl::hamming_dec_impl()
    : gr::sync_block("hamming_dec",
                     gr::io_signature::make(1, 1, sizeof(uint8_t)),
                     gr::io_signature::make(1, 1, sizeof(uint8_t))) {
  is_first = true;
  message_port_register_in(pmt::mp("CR"));
  set_msg_handler(pmt::mp("CR"),
                  boost::bind(&hamming_dec_impl::header_cr_handler, this, _1));
  message_port_register_in(pmt::mp("new_frame"));
  set_msg_handler(pmt::mp("new_frame"),
                  boost::bind(&hamming_dec_impl::new_frame_handler, this, _1));
                  set_tag_propagation_policy(TPP_ALL_TO_ALL);
}
/**
 * @brief Destroy the hamming dec impl object
 *
 */
hamming_dec_impl::~hamming_dec_impl() {}

/**
 * @brief Handles the coding rate received from the header_decoder block.
 *
 * @param cr : coding rate
 */
void hamming_dec_impl::header_cr_handler(pmt::pmt_t cr) {
  m_cr = pmt::to_long(cr);
};

/**
 * @brief Reset the block variables for a new frame.
 *
 * @param id
 */
void hamming_dec_impl::new_frame_handler(pmt::pmt_t id) { is_first = true; };

/**
 * @brief Main function where the actual computation resides
 *
 * @param noutput_items : number of output items
 * @param input_items : input items (i.e. data from deinterleaver)
 * @param output_items : output data
 * @return int
 */
int hamming_dec_impl::work(int noutput_items,
                           gr_vector_const_void_star &input_items,
                           gr_vector_void_star &output_items) {
  const uint8_t *in = (const uint8_t *)input_items[0];
  uint8_t *out = (uint8_t *)output_items[0];

  cr_app = is_first ? 4 : m_cr;
  std::vector<bool> data_nibble(4, 0);
  bool s0, s1, s2 = 0;
  int syndrom = 0;

  std::vector<bool> codeword;

  for (int i = 0; i < noutput_items; i++) {
    codeword = int2bool(in[i], cr_app + 4);
    data_nibble = {codeword[3], codeword[2], codeword[1],
                   codeword[0]}; // reorganized msb-first
    switch (cr_app) {
    case 4:
      if (!(count(codeword.begin(), codeword.end(), true) %
            2)) // Don't correct if even number of errors
        break;
    case 3:
      // get syndrom
      s0 = codeword[0] ^ codeword[1] ^ codeword[2] ^ codeword[4];
      s1 = codeword[1] ^ codeword[2] ^ codeword[3] ^ codeword[5];
      s2 = codeword[0] ^ codeword[1] ^ codeword[3] ^ codeword[6];

      syndrom = s0 + (s1 << 1) + (s2 << 2);

      switch (syndrom) {
      case 5:
        data_nibble[3].flip();
        break;
      case 7:
        data_nibble[2].flip();
        break;
      case 3:
        data_nibble[1].flip();
        break;
      case 6:
        data_nibble[0].flip();
        break;
      default: // either parity bit wrong or no error
        break;
      }
      break;
    case 2:
      s0 = codeword[0] ^ codeword[1] ^ codeword[2] ^ codeword[4];
      s1 = codeword[1] ^ codeword[2] ^ codeword[3] ^ codeword[5];

      if (s0 | s1) {
        GR_LOG_INFO(this->d_logger, "INFO: Erroneous LSB");
      }
      break;
    case 1:
      if (!(count(codeword.begin(), codeword.end(), true) % 2)) {
        GR_LOG_INFO(this->d_logger, "INFO: Erroneous LSB");
      }
      break;
    }
    out[i] = bool2int(data_nibble);
  }
  is_first = false;
  return noutput_items;
}
} // namespace lora_sdr
} /* namespace gr */
