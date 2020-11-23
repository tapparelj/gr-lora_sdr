#ifndef INCLUDED_LORA_hamming_dec_IMPL_H
#define INCLUDED_LORA_hamming_dec_IMPL_H

#include <lora_sdr/hamming_dec.h>

namespace gr {
namespace lora_sdr {

class hamming_dec_impl : public hamming_dec {
private:
  /**
   * @brief Transmission coding rate
   * 
   */
  uint8_t m_cr; 

  /**
   * @brief Coding rate use for the block
   * 
   */
  uint8_t cr_app;

  /**
   * @brief Indicate that it is the first block
   * 
   */
  bool is_first;

  /**
   * @brief Handles the coding rate received from the header_decoder block.
   * 
   * @param cr : coding rate
   */
  void header_cr_handler(pmt::pmt_t cr);

  /**
   * @brief Reset the block variables for a new frame.
   * 
   * @param id 
   */
  void new_frame_handler(pmt::pmt_t id);

public:
  /**
   * @brief Construct a new hamming dec impl object
   *
   */
  hamming_dec_impl();
  /**
   * @brief Destroy the hamming dec impl object
   *
   */
  ~hamming_dec_impl();
  /**
   * @brief Main function
   *
   * @param noutput_items
   * @param input_items
   * @param output_items
   * @return int
   */
  int work(int noutput_items, gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_hamming_dec_IMPL_H */
