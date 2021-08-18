
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "hamming_dec_impl.h"
#include <gnuradio/io_signature.h>
#include "helpers.h"

namespace gr {
namespace lora_sdr {

hamming_dec::sptr hamming_dec::make() {
  return gnuradio::get_initial_sptr(new hamming_dec_impl());
}


/**
 * @brief Construct a new hamming dec impl::hamming dec impl object
 * 
 */
hamming_dec_impl::hamming_dec_impl()
    : gr::sync_block("hamming_dec",
                     gr::io_signature::make(1, 1, sizeof(uint8_t)),
                     gr::io_signature::make(1, 1, sizeof(uint8_t))) {
  set_tag_propagation_policy(TPP_ONE_TO_ONE);
        gr::block::set_thread_priority(96);
}

/**
 * @brief Destroy the hamming dec impl::hamming dec impl object
 *
 */
hamming_dec_impl::~hamming_dec_impl() {}

/**
 * @brief 
 * 
 * @param noutput_items 
 * @param input_items 
 * @param output_items 
 * @return int 
 */
int hamming_dec_impl::work(int noutput_items,
                           gr_vector_const_void_star &input_items,
                           gr_vector_void_star &output_items) {
  const uint8_t *in = (const uint8_t *)input_items[0];
  uint8_t *out = (uint8_t *)output_items[0];
  int nitems_to_process = noutput_items;

  std::vector<tag_t> tags;
  get_tags_in_window(tags, 0, 0, noutput_items,
                     pmt::string_to_symbol("frame_info"));
  if (tags.size()) {
    if (tags[0].offset != nitems_read(0))
      nitems_to_process =
          tags[0].offset -
          nitems_read(0); // only decode codewords until the next frame begin

    else {
      if (tags.size() >= 2)
        nitems_to_process = tags[1].offset - tags[0].offset;

      pmt::pmt_t err = pmt::string_to_symbol("error");
      is_header = pmt::to_bool(pmt::dict_ref(
          tags[0].value, pmt::string_to_symbol("is_header"), err));

      if (!is_header) {
        m_cr = pmt::to_long(
            pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cr"), err));
      }
    }
  }

  cr_app = is_header ? 4 : m_cr;
  std::vector<bool> data_nibble(4, 0);
  bool s0, s1, s2 = 0;
  int syndrom = 0;

  std::vector<bool> codeword;

  for (int i = 0; i < nitems_to_process; i++) {
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
  return nitems_to_process;
}
} // namespace lora_sdr
} /* namespace gr */
