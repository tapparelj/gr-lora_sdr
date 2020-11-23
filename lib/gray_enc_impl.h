#ifndef INCLUDED_LORA_GRAY_ENC_IMPL_H
#define INCLUDED_LORA_GRAY_ENC_IMPL_H
// #define GRLORA_DEBUG
#include <lora_sdr/gray_enc.h>

namespace gr {
namespace lora_sdr {

class gray_enc_impl : public gray_enc {
public:
  /**
   * @brief Construct a new gray enc impl object
   * 
   */
  gray_enc_impl();

  /**
   * @brief Destroy the gray enc impl object
   * 
   */
  ~gray_enc_impl();

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

#endif /* INCLUDED_LORA_GRAY_ENC_IMPL_H */
