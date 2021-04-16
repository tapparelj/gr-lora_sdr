#ifndef INCLUDED_LORA_ADD_CRC_IMPL_H
#define INCLUDED_LORA_ADD_CRC_IMPL_H

#include <lora_sdr/add_crc.h>
#include <lora_sdr/utilities.h>
namespace gr {
namespace lora_sdr {

class add_crc_impl : public add_crc {
private:
/**
 * @brief indicate the presence of a payload CRC
 * 
 */
  bool m_has_crc;            
  
  /**
   * @brief payload data
   * 
   */
  std::vector<uint8_t> m_payload;
  
  /**
   * @brief length of the payload in Bytes
   * 
   */
  uint8_t m_payload_len;          
  
  /**
   * @brief length of the frame in number of gnuradio items
   * 
   */
  int m_frame_len; 
  
  /**
   * @brief  counter of the number of symbol in frame
   * 
   */
  int m_cnt;    

  /**
   * @brief Calculates the crc value for a given byte
   * 
   * @param crcValue : current crc value
   * @param newByte : byte for calculate the crc value for 
   * @return unsigned int 
   */
  unsigned int crc16(unsigned int crcValue, unsigned char newByte);

public:
/**
 * @brief Construct a new add crc impl object
 * 
 * @param has_crc : boolean if crc is turned on or not
 */
  add_crc_impl(bool has_crc);

  /**
   * @brief Destroy the add crc impl object
   * 
   */
  ~add_crc_impl();

  /**
   * @brief Standard gnuradio function for telling the scheduler how many input items are needed
   * 
   * @param noutput_items number of input items
   * @param ninput_items_required minimum items required
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief stanard gnuradio function that does the actual computations
   * 
   * @param noutput_items number of output items
   * @param ninput_items number of input items
   * @param input_items input items (input data)
   * @param output_items output items (output data)
   * @return int 
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};
} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_ADD_CRC_IMPL_H */
