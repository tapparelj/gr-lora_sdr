#ifndef INCLUDED_LORA_DEWHITENING_IMPL_H
#define INCLUDED_LORA_DEWHITENING_IMPL_H

// #define GRLORA_DEBUG
#include <lora_sdr/dewhitening.h>

namespace gr {
namespace lora_sdr {

class dewhitening_impl : public dewhitening {
private:
  /**
   * @brief Payload length in bytes
   *
   */
  int m_payload_len;

  /**
   * @brief indicate the presence of a CRC
   *
   */
  int m_crc_presence;

  /**
   * @brief The offset in the whitening table
   *
   */
  int offset = 0;

  /**
   * @brief The dewhitened bytes
   *
   */
  std::vector<uint8_t> dewhitened;

  /**
   * @brief Handles the payload length received from the header_decoder block.
   *
   * @param payload_len : payload length
   */
  void header_pay_len_handler(pmt::pmt_t payload_len);

  /**
   * @brief Reset the block variables for a new frame.
   *
   * @param id
   */
  void new_frame_handler(pmt::pmt_t id);

  /**
   * @brief Receive indication on the CRC presence
   *
   * @param crc_presence : control message if add_crc is active
   */
  void header_crc_handler(pmt::pmt_t crc_presence);

public:
  /**
   * @brief Construct a new dewhitening impl object
   *
   */
  dewhitening_impl();

  /**
   * @brief Destroy the dewhitening impl object
   *
   */
  ~dewhitening_impl();

  /**
   * @brief standard gnuradio function to tell the system when to start work
   *
   * @param noutput_items : number of output items
   * @param ninput_items_required : number of input items required
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main dewhitining function
   *
   * @param noutput_items : number of output items 
   * @param ninput_items : number of input items
   * @param input_items : input data (i.e. header_decoder stage)
   * @param output_items : output data
   * @return int
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_DEWHITENING_IMPL_H */
