#ifndef INCLUDED_LORA_GRAY_DECODE_IMPL_H
#define INCLUDED_LORA_GRAY_DECODE_IMPL_H

#include <lora_sdr/gray_decode.h>

namespace gr {
namespace lora_sdr {

class gray_decode_impl : public gray_decode {
private:
 /**
  * @brief Sampling rate
  * 
  */
  uint8_t m_sf;

public:
  /**
   * @brief Construct a new gray decode impl object
   *
   * @param sf : sampling rate
   */
  gray_decode_impl(uint8_t sf);

  /**
   * @brief Destroy the gray decode impl object
   *
   */
  ~gray_decode_impl();

  /**
   * @brief Main function where the actual computation resides
   *
   * @param noutput_items : number of output items
   * @param input_items : input items (i.e. fft_demod)
   * @param output_items : output data
   * @return int
   */
  int work(int noutput_items, gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
};
} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_GRAY_DECODE_IMPL_H */
