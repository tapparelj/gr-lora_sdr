
#ifndef INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H
#define INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H
// #define GRLORA_DEBUG
// #define GRLORA_MEASUREMENTS

#include <fstream>
#include <gnuradio/io_signature.h>
#include <iostream>
#include <lora_sdr/fft_demod.h>
#include <lora_sdr/utilities.h>
#include <volk/volk.h>
namespace gr {
namespace lora_sdr {

class fft_demod_impl : public fft_demod {
private:
  /**
   * @brief Bandwidth
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
   * @brief Coding rate
   *
   */
  uint8_t m_cr;

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
   * @brief integer part of the CFO
   *
   */
  int CFOint;

  // variables used to perform the FFT demodulation
  /**
   * @brief Reference upchirp
   *
   */
  std::vector<gr_complex> m_upchirp;

  /**
   * @brief Reference downchirp
   *
   */
  std::vector<gr_complex> m_downchirp;
  /**
   * @brief Dechirped symbol
   *
   */
  std::vector<gr_complex> m_dechirped;

  /**
   * @brief Result of the FFT
   *
   */
  std::vector<gr_complex> m_fft;

  /**
   * @brief Stores the value to be outputted once a
  full bloc has been received
   *
   */
  std::vector<uint32_t> output;

  /**
   * @brief Indicate that the first block hasn't been fully received
   *
   */
  bool is_first;

  /**
   * @brief The number of lora symbol in one block
   *
   */
  uint8_t block_size;

  /**
   * @brief Indicate that the coding rate has been given by the
  header_decoder block
   *
   */
  bool received_cr;

  /**
   * @brief Indicate that the crc presence has been given by the
  header_decoder block
   *
   */
  bool received_crc;

  /**
   * @brief Indicate that the payload length has been given by the
   * header_decoder block
   *
   */
  bool received_pay_len;
#ifdef GRLORA_MEASUREMENTS
  std::ofstream energy_file;
#endif

  /**
   * @brief Recover the lora symbol value using argmax of the dechirped symbol
   * FFT.
   *
   * @param samples The pointer to the symbol beginning.
   * @return int32_t
   */
  int32_t get_symbol_val(const gr_complex *samples);

  /**
   * @brief Reset the block variables when a new lora packet needs to be
   * decoded.
   *
   * @param id
   */
  void new_frame_handler(pmt::pmt_t id);

  /**
   * @brief Handles the reception of the coding rate received by the
   * header_decoder block.
   *
   * @param cr
   */
  void header_cr_handler(pmt::pmt_t cr);

public:
  /**
   * @brief Construct a new fft demod impl object
   *
   * @param samp_rate
   * @param bandwidth
   * @param sf
   * @param impl_head
   */
  fft_demod_impl(float samp_rate, uint32_t bandwidth, uint8_t sf,
                 bool impl_head);
  /**
   * @brief Destroy the fft demod impl object
   *
   */
  ~fft_demod_impl();

  /**
   * @brief
   *
   * @param noutput_items
   * @param ninput_items_required
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function
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

#endif /* INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H */
