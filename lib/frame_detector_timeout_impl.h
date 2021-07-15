/**
 * @file frame_detector_timeout_impl.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-06-21
 *
 *
 */
#ifndef INCLUDED_LORA_SDR_FRAME_DETECTOR_TIMEOUT_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_DETECTOR_TIMEOUT_IMPL_H

#include <lora_sdr/frame_detector_timeout.h>
extern "C" {
#include "kiss_fft.h"
}

#define GRLORA_DEBUGV
namespace gr {
namespace lora_sdr {

class frame_detector_timeout_impl : public frame_detector_timeout {
private:
  /**
   * @brief State the frame finder can be in
   * - FIND_PREAMLBE : find the preamble
   * - SEND_PREAMBLE : send the buffered preamble symbols
   * - SEND_FRAME : send frame
   *
   */
  enum State { FIND_PREAMBLE, SEND_PREAMBLE, SEND_FRAME };

  /**
   * @brief Current state of the frame finder
   *
   */
  uint8_t m_state;

  /**
   * @brief Spreading factor
   *
   */
  uint8_t m_sf;

  /**
   * @brief Number of bytes we should send after detection
   *
   */
  uint16_t m_n_bytes;

  uint16_t m_store_n_bytes;

  /**
   * @brief Number of samples per LoRa symbol
   *
   */
  uint32_t m_samples_per_symbol;

  /**
   * @brief 2^sf
   *
   */
  uint32_t m_N;

  /**
   * @brief the reference downchirp
   *
   */
  std::vector<gr_complex> m_downchirp;

  /**
   * @brief the dechirped symbols on which we need to perform the FFT.
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
   * @briefiterator used to find max and argmax of FFT
   *
   */
  std::vector<float>::iterator m_max_it;

  /**
   * @brief vector containing the magnitude of the FFT.
   *
   */
  std::vector<float> m_dfts_mag;

  /**
   * @brief value of previous lora demodulated symbol
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
   * @brief Temporary memory vector
   *
   */
  std::vector<gr_complex> buffer;

  /**
   * @brief  LoRa symbol count
   *
   */
  uint16_t symbol_cnt;

  /**
   * @brief lora symbols per second
   *
   */
  double m_symbols_per_second;

  /**
   * @brief Transmission sampling rate
   *
   */
  uint32_t m_samp_rate;

  /**
   * @brief Transmission bandwidth (Works only for samp_rate=bw)
   *
   */
  uint32_t m_bw;

  /**
   * @brief Counter for counting the number of bytes we have sent
   *
   */
  uint16_t m_cnt;

  bool m_detect_second_packet;

  /**
   * @brief Get the symbol object value (aka decoded LoRa symbol value)
   * Function consumes vectors of length m_N
   *
   * @param input : complex samples
   * @return int32_t : LoRa symbol value
   */
  int32_t get_symbol_val(const gr_complex *input);

public:
  /**
   * @brief Construct a new frame detector impl object
   *
   * @param samp_rate : sampling rate
   * @param bandwidth : bandwith
   * @param sf : spreading factor
   * @param n_bytes : number of bytes to send after preamble detection
   */
  frame_detector_timeout_impl(uint8_t sf, uint32_t smap_rate, uint32_t bw,
                              uint8_t n_bytes);

  /**
   * @brief Destroy the frame detector impl object
   *
   */
  ~frame_detector_timeout_impl();

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

#endif /* INCLUDED_LORA_SDR_FRAME_DETECTOR_TIMEOUT_IMPL_H */
