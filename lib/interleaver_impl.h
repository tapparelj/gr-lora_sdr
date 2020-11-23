#ifndef INCLUDED_LORA_INTERLEAVER_IMPL_H
#define INCLUDED_LORA_INTERLEAVER_IMPL_H

#include <lora_sdr/interleaver.h>
// #define GRLORA_DEBUG

namespace gr {
namespace lora_sdr {

class interleaver_impl : public interleaver {
private:
  /**
   * @brief Transmission coding rate
   *
   */
  uint8_t m_cr;

  /**
   * @brief Transmission spreading factor
   *
   */
  uint8_t m_sf;

  /**
   * @brief count the number of codewords
   *
   */
  uint32_t cw_cnt;

  /**
   * @brief
   *
   * @param message
   */
  void msg_handler(pmt::pmt_t message);

public:
  /**
   * @brief Construct a new interleaver impl object
   *
   * @param cr coding rate
   * @param sf sampling rate
   */
  interleaver_impl(uint8_t cr, uint8_t sf);

  /**
   * @brief Destroy the interleaver impl object
   *
   */
  ~interleaver_impl();

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

#endif /* INCLUDED_LORA_INTERLEAVER_IMPL_H */
