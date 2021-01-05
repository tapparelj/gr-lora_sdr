#ifndef INCLUDED_LORA_SDR_WHITENING_IMPL_H
#define INCLUDED_LORA_SDR_WHITENING_IMPL_H

#include <lora_sdr/whitening.h>
#include <lora_sdr/api.h>
namespace gr {
namespace lora_sdr {

class whitening_impl : public whitening {
private:
  /**
   * @brief PMT message to indicate that a new message (input data) has to be
   * whitened
   *
   */
  bool new_message;

  /**
   * @brief Variables that stores the payload bytes
   *
   */
  std::vector<uint8_t> m_payload;

  /**
   * @brief Function that waits for the input message, if received copy its to
   * m_payload to be used in work function
   *
   * @param message : string input data
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
   * @param ninput_items_required 
   */

  void forecast(int noutput_items, gr_vector_int &ninput_items_required);
  /**
   * @brief 
   * 
   * @param noutput_items 
   * @param ninput_items 
   * @param input_items 
   * @param output_items 
   * @return int 
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_WHITENING_IMPL_H */
