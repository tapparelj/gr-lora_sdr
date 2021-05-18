#ifndef INCLUDED_LORA_DEINTERLEAVER_IMPL_H
#define INCLUDED_LORA_DEINTERLEAVER_IMPL_H

// #define GRLORA_DEBUG
#include <lora_sdr/deinterleaver.h>

namespace gr {
namespace lora_sdr {

class deinterleaver_impl : public deinterleaver {
private:
  /**
   * @brief Transmission Spreading factor
   *
   */
  uint8_t m_sf;

  /**
   * @brief Transmission Coding rate
   *
   */
  uint8_t m_cr;

  /**
   * @brief Spreading factor to use to deinterleave
   *
   */
  uint8_t sf_app;

  /**
   * @brief Length of a codeword
   *
   */
  uint8_t cw_len;

  /**
   * @brief Indicate that we need to deinterleave the first block with the
   * default header parameters (cr=4/8, reduced rate)
   *
   */
  bool m_is_header;

public:
  /**
   * @brief Construct a new deinterleaver impl object
   *
   * @param sf : sampling rate
   */
  deinterleaver_impl(uint8_t sf);

  /**
   * @brief Destroy the deinterleaver impl object
   *
   */
  ~deinterleaver_impl();

  /**
   * @brief Standard gnuradio function to tell the system with
   *
   * @param noutput_items : number of output items
   * @param ninput_items_required : number of required output items
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function where the actual computation is done
   *
   * @param noutput_items : number of output items
   * @param ninput_items : number of input items
   * @param input_items : input (i.e gray demapping output)
   * @param output_items : output data
   * @return int
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_DEINTERLEAVER_IMPL_H */
