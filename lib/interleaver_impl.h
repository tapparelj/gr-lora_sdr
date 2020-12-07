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
   * @brief variable that counts the number of codewords
   *
   */
  uint32_t cw_cnt;

  /**
   * @brief PMT input message handler.
   * Handles the pmt message (i.e. input data)
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
   * @brief Standard gnuradio function to ensure a number of input items are received before continuing
   *
   * @param noutput_items : number of input items
   * @param ninput_items_required : number of requires input items = 1
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function that does the actual computation of the interleaver.
   * 
   *
   * @param noutput_items : number of output items
   * @param ninput_items : number of input items
   * @param input_items : the data of the input items (i.e hamming encoding stage)
   * @param output_items : output data
   * @return int
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_INTERLEAVER_IMPL_H */
