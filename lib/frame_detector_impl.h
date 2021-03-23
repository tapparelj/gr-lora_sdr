/**
 * @file frame_detector_impl.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-03-23
 *
 *
 */
#ifndef INCLUDED_LORA_SDR_FRAME_DETECTOR_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_DETECTOR_IMPL_H

#include <lora_sdr/frame_detector.h>
extern "C" {
#include "kiss_fft.h"
}

namespace gr {
namespace lora_sdr {

class frame_detector_impl : public frame_detector {
private:

  /**
   * @brief State the frame finder can be in
   * - FIND_PREAMLBE : find the preamble
   * - FIND_END_FRAME : find the end of the frame
   */
  enum State { FIND_PREAMBLE, FIND_END_FRAME};


  /**
   * @brief Current state of the frame finder
   *
   */
  uint8_t m_state;

  /**
   * @brief Bandwith
   *
   */
  uint32_t m_bw;

  /**
   * @brief Sampling rate
   *
   */
  uint32_t m_samp_rate;

  /**
   * @brief Spreading factor
   *
   */
  uint8_t m_sf;

  /**
   * @brief Number of bins in each lora Symbol
   *
   */
  uint32_t m_number_of_bins;

  /**
   * @brief Number of samples received per lora symbols
   *
   */
  uint32_t m_samples_per_symbol;

  /**
   * @brief Reference downchirp
   *
   */
  std::vector<gr_complex> m_downchirp;

  /**
   * @brief input of the FFT
   *
   */
  kiss_fft_cpx *cx_in;

  /**
   * @brief output of the FFT
   *
   */
  kiss_fft_cpx *cx_out;

  /**
   * @brief Number of symbols already received
   *
   */
  int32_t symbol_cnt;

  /**
   * @brief value of previous lora symbol
   *
   */
  int32_t bin_idx;

  /**
   * @brief value of newly demodulated symbol
   *
   */
  int32_t bin_idx_new;

  /**
   * @brief Number of consecutive upchirps in preamble
   *
   */
  uint32_t n_up;

public:
  /**
   * @brief Construct a new frame detector impl object
   *
   */
  frame_detector_impl(float samp_rate, uint32_t bandwidth, uint8_t sf);

  /**
   * @brief Destroy the frame detector impl object
   *
   */
  ~frame_detector_impl();

  /**
   * @brief
   *
   * @param noutput_items : number of output items
   * @param ninput_items_required : required input items (how many items must we
   * have for we can do something)
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief General work function.
   * Main gnuradio function that does the heavy lifting
   *
   * @param noutput_items : number of output items
   * @param ninput_items : number of input items
   * @param input_items : input items
   * @param output_items : output items
   * @return int
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_DETECTOR_IMPL_H */
