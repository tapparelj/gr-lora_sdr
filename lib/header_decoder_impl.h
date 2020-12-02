
#ifndef INCLUDED_LORA_HEADER_DECODER_IMPL_H
#define INCLUDED_LORA_HEADER_DECODER_IMPL_H

#include <lora_sdr/header_decoder.h>

namespace gr {
namespace lora_sdr {

class header_decoder_impl : public header_decoder {
private:
  /**
   * @brief size of the header in nibbles
   *
   */
  const uint8_t header_len = 5;

  /**
   * @brief Specify if we use an explicit or implicit header
   *
   */
  bool m_impl_header;

  /**
   * @brief The payload length in bytes
   *
   */
  uint8_t m_payload_len;

  /**
   * @brief Specify the usage of a payload CRC
   *
   */
  bool m_has_crc;

  /**
   * @brief Coding rate
   *
   */
  uint8_t m_cr;

  /**
   * @brief The header checksum received in the header
   *
   */
  uint8_t header_chk;

  /**
   * @brief The number of payload nibbles received
   *
   */
  uint32_t pay_cnt;

  /**
   * @brief The number of data nibbles to output
   *
   */
  uint32_t nout;

  /**
   * @brief Indicate that we need to decode the header
   *
   */
  bool is_first;

  /**
   * @brief Reset the block variables for a new frame.
   *
   * @param id
   */
  void new_frame_handler(pmt::pmt_t id);

public:
  /**
   * @brief Construct a new header decoder impl object
   *
   * @param impl_head : boolean if implicit header mode is on or off
   * @param cr : coding rate
   * @param pay_len : payload length
   * @param has_crc : boolean if crc stage is active or not
   */
  header_decoder_impl(bool impl_head, uint8_t cr, uint32_t pay_len,
                      bool has_crc);

  /**
   * @brief Destroy the header decoder impl object
   *
   */
  ~header_decoder_impl();

  /**
   * @brief standard gnuradio function to tell the system when to start work
   *
   * @param noutput_items : number of output items
   * @param ninput_items_required : number of required input items
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function where the actual computation resides
   *
   * @param noutput_items : number of output items
   * @param ninput_items : number of input items
   * @param input_items : input data (i.e. hamming decoder stage)
   * @param output_items : output data
   * @return int
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};
} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_HEADER_DECODER_IMPL_H */
