

#ifndef INCLUDED_LORA_WHITENING_IMPL_H
#define INCLUDED_LORA_WHITENING_IMPL_H

#include <lora_sdr/whitening.h>

namespace gr {
namespace lora_sdr {

class whitening_impl : public whitening {
private:
  /**
   * @brief indicate that a new message has to be whitened
   * 
   */
  bool new_message; 

  /**
   * @brief store the payload bytes
   * 
   */
  std::vector<uint8_t> m_payload;  

  /**
   * @brief 
   * 
   * @param message 
   */
  void msg_handler(pmt::pmt_t message);

public:
  /**
   * @brief Construct a new whitening impl object
   * 
   */
  whitening_impl();
  /**
   * @brief Destroy the whitening impl object
   * 
   */
  ~whitening_impl();

  /**
   * @brief 
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

#endif /* INCLUDED_LORA_WHITENING_IMPL_H */
