#ifndef INCLUDED_LORA_SDR_RH_RF95_HEADER_IMPL_H
#define INCLUDED_LORA_SDR_RH_RF95_HEADER_IMPL_H

#include <lora_sdr/RH_RF95_header.h>

namespace gr {
namespace lora_sdr {

class RH_RF95_header_impl : public RH_RF95_header {
private:
  /**
   * @brief radiohead specific header field "to"
   *
   */
  char m_to;

  /**
   * @brief radiohead specific header field "from"
   *
   */
  char m_from;

  /**
   * @brief radiohead specific header field "id"
   *
   */
  char m_id;

  /**
   * @brief radiohead specific header field "flags"
   *
   */
  char m_flags;

  /**
   * @brief <payload bytes
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
   * @brief Construct a new rh rf95 header impl object
   *
   * @param _to
   * @param _from
   * @param _id
   * @param _flags
   */
  RH_RF95_header_impl(uint8_t _to, uint8_t _from, uint8_t _id, uint8_t _flags);
  /**
   * @brief Destroy the rh rf95 header impl object
   *
   */
  ~RH_RF95_header_impl();

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

#endif /* INCLUDED_LORA_SDR_RH_RF95_HEADER_IMPL_H */
