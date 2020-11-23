#ifndef INCLUDED_LORA_ADD_CRC_IMPL_H
#define INCLUDED_LORA_ADD_CRC_IMPL_H

#include <lora_sdr/add_crc.h>

namespace gr {
namespace lora_sdr {

class add_crc_impl : public add_crc {
private:
  /**
   * @brief Indicate the presence of a payload CRC
   *
   */
  bool m_has_crc;

  /**
   * @brief The payload data itself
   *
   */
  std::vector<uint8_t> m_payload;

  /**
   * @brief The length of the payload in bytes
   *
   */
  uint8_t m_payload_len;

  /**
   * @brief Message handler, handles all the control messages
   *
   * @param message :pmt message
   */
  void msg_handler(pmt::pmt_t message);
  
  /**
   * @brief CRC16, add 16 bit CRC to the payload.
   *
   * @param crcValue :
   * @param newByte :
   * @return unsigned int
   */
  unsigned int crc16(unsigned int crcValue, unsigned char newByte);

public:
  /**
   * @brief Construct a new add crc impl object
   *
   * @param has_crc
   */
  add_crc_impl(bool has_crc);

  /**
   * @brief Destroy the add crc impl object
   *
   */
  ~add_crc_impl();

  /**
   * @brief Where all the action really happens
   *
   * @param noutput_items : number of output items
   * @param ninput_items_required : number of required input items
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function of the add_crc module, this module will add Cyclic
   * Redundancy Check (CRC) to the payload to be able to detect more bit errors.
   *
   * @param noutput_items : number of output items
   * @param ninput_items : number of input items
   * @param input_items  : vector containing the input items
   * @param output_items : vector containting the output items
   * @return int
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};
} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_ADD_CRC_IMPL_H */
