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
  enum State { FIND_PREAMBLE, SEND_FRAMES, FIND_END_FRAME };

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
  uint32_t m_N;

  /**
   * @brief Number of samples received per lora symbols
   *
   */
  uint32_t m_samples_per_symbol;

  /**
   * @brief reference downchirp
   *
   */
  std::vector<gr_complex> m_downchirp;

  /**
   * @brief the dechirped symbols on which we need to perform the FF
   *
   */
  std::vector<gr_complex> m_dechirped;

  /**
   * @brief the output of the FFT
   *
   */
  std::vector<gr_complex> cx_out;

  /**
   * @brief the configuration of the FFT
   *
   */
  kiss_fft_cfg fft_cfg;
  /**
   * @brief decimated input
   *
   */
  std::vector<gr_complex> m_input_decim;

  /**
   * @brief iterator used to find max and argmax of FFT
   *
   */
  std::vector<float>::iterator m_max_it;

  /**
   * @brief vector containing the magnitude of the FFT.
   *
   */
  std::vector<float> m_dfts_mag;

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

  /**
   * @brief Temproary memory vector to hold samples values
   *
   */
  std::vector<gr_complex> mem_vec;

  /**
   * @brief Treshold value to compare to
   *
   */
  float m_threshold;

  /**
   * @brief Upsampling factor to use
   *
   */
  uint8_t m_os_factor;

  /**
   * @brief Current power
   *
   */
  float m_power;

  /**
   * @brief Number of samples to take as margin
   *
   */
  float m_margin;

  /**
   * @brief number of symbols on which the fft will be made
   *
   */
  int m_fft_symb;

public:
  /**
   * @brief Construct a new frame detector impl object
   *
   * @param samp_rate : sampling rate
   * @param bandwidth : bandwith
   * @param sf : spreading factor
   */
  frame_detector_impl(float samp_rate, uint32_t bandwidth, uint8_t sf);

  /**
   * @brief Destroy the frame detector impl object
   *
   */
  ~frame_detector_impl();

  /**
   * @brief Standard gnuradio function to forecast the number of items needed in
   * order for the file to function
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
