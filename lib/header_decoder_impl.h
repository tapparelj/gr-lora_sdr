
#ifndef INCLUDED_LORA_HEADER_DECODER_IMPL_H
#define INCLUDED_LORA_HEADER_DECODER_IMPL_H

#include <lora_sdr/header_decoder.h>

namespace gr {
namespace lora_sdr {

class header_decoder_impl : public header_decoder {
private:
  /**
   * @brief ize of the header in nibbles
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
   * @brief
   *
   */
  uint8_t header_chk; ///< The header checksum received in the header

  /**
   * @brief
   *
   */
  uint32_t pay_cnt; ///< The number of payload nibbles received

  /**
   * @brief
   *
   */
  uint32_t nout; ///< The number of data nibbles to output
  /**
   * @brief
   *
   */
  bool is_header; ///< Indicate that we need to decode the header

  /**
   * @brief Reset the block variables for a new frame.
   *
   */
  void new_frame_handler();

  /**
   * @brief publish decoding information contained in the header or provided to
   * the block
   *
   * @param cr
   * @param pay_len
   * @param crc
   * @param err
   */
  void publish_frame_info(int cr, int pay_len, int crc, int err);

public:
  /**
   * @brief Construct a new header decoder impl object
   *
   * @param impl_head
   * @param cr
   * @param pay_len
   * @param has_crc
   */
  header_decoder_impl(bool impl_head, uint8_t cr, uint32_t pay_len,
                      bool has_crc);
  /**
   * @brief Destroy the header decoder impl object
   *
   */
  ~header_decoder_impl();

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

#endif /* INCLUDED_LORA_HEADER_DECODER_IMPL_H */
