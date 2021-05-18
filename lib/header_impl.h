#ifndef INCLUDED_LORA_HEADER_IMPL_H
#define INCLUDED_LORA_HEADER_IMPL_H

#include <lora_sdr/header.h>

namespace gr {
namespace lora_sdr {

class header_impl : public header {
private:
  /**
   * @brief boolean variable to indicate implicit header mode is used
   *
   */
  bool m_impl_head;

  /**
   * @brief boolean variable to indicate the presence of a payload crc
   *
   */
  bool m_has_crc;

  /**
   * @brief Transmission coding rate
   *
   */
  uint8_t m_cr;

  /**
   * @brief Payload length (i.e input data length)
   *
   */
  uint8_t m_payload_len;

  /**
   * @brief count the processes nibbles in a frame
   *
   */
  uint m_cnt_nibbles;

  /**
   * @brief count the number of explicit header nibbles output
   *
   */
  uint m_cnt_header_nibbles;

  /**
   * @brief contain the header to prepend
   *
   */
  std::vector<uint8_t> m_header;

  /**
   * @brief
   *
   */
  std::vector<tag_t> m_tags;

  /**
   * @brief Function that handles on the input PMT message (i.e. input data from
   * data source)
   *
   * @param message pmt message
   */
  void msg_handler(pmt::pmt_t message);

public:
  /**
   * @brief Construct a new header impl object
   *
   * @param impl_head boolean variable to indicate implicit header mode is used
   * @param has_crc boolean variable to indicate the presence of a payload crc
   * @param cr Transmission coding rate
   */
  header_impl(bool impl_head, bool has_crc, uint8_t cr);

  /**
   * @brief Destroy the header impl object
   *
   */
  ~header_impl();
  /**
   * @brief Gnuradio forecast function which tells the
   * gnuradio system how many items are needed before it can continue to the
   * work function
   *
   * @param noutput_items : number of output items
   * @param ninput_items_required : number of required output items before
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function where the actual computation is done.
   * If impl_head is set to true the output will be  the payload added with an header
   * 
   * @param noutput_items : number of ouput items
   * @param ninput_items : number of input items
   * @param input_items : input items (output of whitening stage)
   * @param output_items : output items (added header if applicable)
   * @return int 
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_HEADER_IMPL_H */
