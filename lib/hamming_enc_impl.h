#ifndef INCLUDED_LORA_HAMMING_ENC_IMPL_H
#define INCLUDED_LORA_HAMMING_ENC_IMPL_H

#include <lora_sdr/hamming_enc.h>

namespace gr {
namespace lora_sdr {

class hamming_enc_impl : public hamming_enc {
private:
  /**
   * @brief Transmission coding rate
   * 
   */
  uint8_t m_cr; 

  /**
   * @brief Transmission spreading factor
   * 
   */
  uint8_t m_sf; 

public:
  /**
   * @brief Construct a new hamming enc impl object
   *
   * @param cr
   * @param sf
   */
  hamming_enc_impl(uint8_t cr, uint8_t sf);

  /**
   * @brief Destroy the hamming enc impl object
   *
   */
  ~hamming_enc_impl();

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

#endif /* INCLUDED_LORA_HAMMING_ENC_IMPL_H */
