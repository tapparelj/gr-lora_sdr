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
  bool is_header;

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
   * @brief Main function where the actual computation resides
   * 
   * @param noutput_items : number of output items
   * @param input_items : input items (i.e. data from deinterleaver)
   * @param output_items : output data
   * @return int
   */
  int work(int noutput_items, gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_hamming_dec_IMPL_H */
