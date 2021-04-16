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
#include <gnuradio/io_signature.h>
#include <math.h>
extern "C" {
#include "kiss_fft.h"
}
//#define GRLORA_log

namespace gr {
namespace lora_sdr {

    /**
     * @brief Simple data holder class for memory vec
     * 
     */
    class Temporary_buffer{
        /**
         * @brief Temporary vector containting data elements
         * 
         */
        std::vector<gr_complex> temp_mem_vec;
    public:
        /**
         * @brief Wrapper around the push_back function
         * 
         */
        void push_value(gr_complex);
        /**
         * @brief Wrapper function for the clear function
         * 
         */
        void clear();
        /**
         * @brief Wrapper for the erase functoin
         * 
         */
        void erase(int);
        /**
         * @brief Wrapper for the empty function
         * 
         * @return true : memory is empty
         * @return false : memory is not empty
         */
        bool empty();
        /**
         * @brief Wrapper of the size function
         * 
         * @return int : number of elements in the vector
         */
        int get_size();
        /**
         * @brief Get the value of vector at point int
         * 
         * @return gr_complex 
         */
        gr_complex get_value(int);
        /**
         * @brief Set the reserve object
         * 
         */
        void set_reserve(int);
    } temp_mem;


class frame_detector_impl : public frame_detector {
private:
  /**
   * @brief State the frame finder can be in
   * - FIND_PREAMLBE : find the preamble
   * - FIND_END_FRAME : find the end of the frame
   */
  enum State { FIND_PREAMBLE, SEND_FRAMES};


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
   * @brief oversampling factor
   *
   */
  uint8_t m_os_factor;

  /**
   * @brief detection threshold
   *
   */
  double m_threshold;

  /**
   * @brief number of symbols on which the fft will be made
   *
   */
  int32_t m_fft_symb;

  /**
   * @brief margin in the input buffer that will be output when a detection
   * occurs [number of symbols]
   *
   */
  int32_t m_margin;

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
   * @brief downsampled input
   *
   */
  std::vector<gr_complex> m_input_downsampled;

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
  Temporary_buffer mem_vec;

  /**
   * @brief  LoRa symbol count
   *
   */
  uint16_t symbol_cnt;

  /**
   * @brief Power of a detected LoRa preamble to compare against
   *
   */
  float m_power;

  /**
   * @brief Value to devide by when there is no noise in the system (recommended value 2)
   *
   */
  uint16_t m_signal_power_decim;

#ifdef GRLORA_log
  std::ofstream output_log_before;
  std::ofstream output_log_after;
#endif

/**
 * @brief Get the symbol object value (aka decoded LoRa symbol value)
 * 
 * @param input : complex samples
 * @return int32_t : LoRa symbol value
 */
  int32_t get_symbol(gr_complex *input);

/**
 * @brief Checks if current samples have the right 
 * 
 * @param input 
 * @return true : we are in a LoRa frame
 * @return false : we are not in a LoRa frame
 */
  bool check_in_frame(gr_complex *input);

/**
 * @brief Calculates the LoRa frame peak power
 * 
 * @param input : input samples
 * @return float : peak power
 */
  float calc_power(gr_complex *input);

/**
 * @brief Set the current LoRa frame power
 *
 * @param input : complex samples
 */
  void set_power(gr_complex *input);

public:
  /**
   * @brief Construct a new frame detector impl object
   *
   * @param samp_rate : sampling rate
   * @param bandwidth : bandwith
   * @param sf : spreading factor
   * @param threshold : threshold value to use
   */
  frame_detector_impl(float samp_rate, uint32_t bandwidth, uint8_t sf,uint32_t threshold);

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