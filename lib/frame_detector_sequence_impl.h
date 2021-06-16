/**
 * @file frame_detector_sequence_impl.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-06-14
 *
 *
 */

#ifndef INCLUDED_LORA_SDR_FRAME_DETECTOR_SEQUENCE_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_DETECTOR_SEQUENCE_IMPL_H

#include <lora_sdr/frame_detector_sequence.h>
extern "C" {
#include "kiss_fft.h"
}
#define GRLORA_DEBUGV
namespace gr {
namespace lora_sdr {

class frame_detector_sequence_impl : public frame_detector_sequence {
private:
  /**
   * @brief State the frame finder can be in
   * - FIND_PREAMLBE : find the preamble
   * - SEND_BUFFER : send the buffered input
   * - SEND_PREAMBLE : send the preamble
   * - SEND_FRAME : send frame and serach for end of frame
   * -SEND_END_FRAME : TODO: logic surrounding CRC check
   */
  enum State { FIND_PREAMBLE, SEND_BUFFER, SEND_PREAMBLE, SEND_FRAME, SEND_END_FRAME};
  
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
   * @brief The number of connective symbols form the end of the packet.
   * 
   */
  uint8_t m_n_seq;

  /**
   * @brief Counter for counting if we are past the net identifier and
   * downchirps once we have found the preamble
   *
   */
    int m_cnt;

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
 * @brief Construct a new frame detector sequence impl object
 * 
 * @param sf : spreading factor
 * @param samp_rate : sampling rate
 * @param bw : bandwith 
 * @param n_seq : number of consecitive symbols for the end
 */
  frame_detector_sequence_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw,
                               uint8_t n_seq);
  
  /**
   * @brief Destroy the frame detector sequence impl object
   * 
   */
  ~frame_detector_sequence_impl();

  /**
   * @brief Function to tell scheduler how many items we need 
   * 
   * @param noutput_items : number of output items
   * @param ninput_items_required : number of required input itens
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief General function where all the stuff happens
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

#endif /* INCLUDED_LORA_SDR_FRAME_DETECTOR_SEQUENCE_IMPL_H */
