#ifndef INCLUDED_LORA_HEADER_IMPL_H
#define INCLUDED_LORA_HEADER_IMPL_H

#include <lora_sdr/header.h>

namespace gr {
namespace lora_sdr {

class header_impl : public header {
private:
  /**
   * @brief indicate if the header is implicit
   * 
   */
  bool m_impl_head;     
  
  /**
   * @brief indicate the presence of a payload crc
   * 
   */
  bool m_has_crc;      
  
  /**
   * @brief Transmission coding rate 
   * 
   */
  uint8_t m_cr;          
  
  /**
   * @brief Payload length
   * 
   */
  uint8_t m_payload_len; 

  /**
   * @brief M
   * 
   * @param message pmt message
   */
  void msg_handler(pmt::pmt_t message);

public:
  /**
   * @brief Construct a new header impl object
   * 
   * @param impl_head boolean if implicit header mode is on or off
   * @param has_crc boolean if crc stage is active or not
   * @param cr coding rate
   */
  header_impl(bool impl_head, bool has_crc, uint8_t cr);
  
  /**
   * @brief Destroy the header impl object
   * 
   */
  ~header_impl();

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

#endif /* INCLUDED_LORA_HEADER_IMPL_H */
