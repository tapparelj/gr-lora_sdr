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

#endif /* INCLUDED_LORA_GRAY_DECODE_IMPL_H */
