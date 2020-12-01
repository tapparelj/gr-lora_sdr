
#ifndef INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H

#include <fstream>
#include <gnuradio/io_signature.h>
#include <iostream>
#include <lora_sdr/frame_sync.h>
#include <lora_sdr/utilities.h>
#include <volk/volk.h>
extern "C" {
#include "kiss_fft.h"
}

namespace gr {
namespace lora_sdr {

class frame_sync_impl : public frame_sync {
private:
  /**
   * @brief Decoder states:
   * - DETECT : Detect preamble
   * - SYNC : synchronize integer part STO,CFO
   * - FRAC_CFO_CORREC : 
   * - STOP
   *
   */
  enum DecoderState { DETECT, SYNC, FRAC_CFO_CORREC, STOP };
  /**
   * @brief Sync states:
   * - NET_ID1
   * - NET_ID2
   * - DOWNCHIRP1
   * - DOWNCHIRP2
   * - QUARTER_DOWN
   *
   */
  enum SyncState { NET_ID1, NET_ID2, DOWNCHIRP1, DOWNCHIRP2, QUARTER_DOWN };

  /**
   * @brief Current state of the synchronization
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
   * @brief Coding rate
   *
   */
  uint8_t m_cr;

  /**
   * @brief Payload length
   *
   */
  uint32_t m_pay_len;

  /**
   * @brief CRC presence
   *
   */
  uint8_t m_has_crc;

  /**
   * @brief Use implicit header mode
   *
   */
  bool m_impl_head;

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
   * @brief Indicate that the payload length has been given by
  the header_decoder block
   *
   */
  bool received_pay_len;

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
   * @brief number of payload loar symbols
   *
   */
  uint32_t symb_numb;

  /**
   * @brief downsampled input
   *
   */
  std::vector<gr_complex> in_down;

  /**
   * @brief Reference downchirp
   *
   */
  std::vector<gr_complex> m_downchirp;

  /**
   * @brief Reference upchirp
   *
   */
  std::vector<gr_complex> m_upchirp;

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
   * @brief Number of integer symbol to skip after
  consecutive upchirps
   *
   */
  uint8_t symbols_to_skip;

  /**
   * @brief network identifier 1
   *
   */
  uint32_t net_id_1;

  /**
   * @brief network identifier 2
   *
   */
  uint32_t net_id_2;

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
   * @brief Number of items to consume after each iteration of
  the general_work function
   *
   */
  int items_to_consume;

  /**
   * @brief vector containing the preamble
  upchirps without any synchronization
   *
   */
  std::vector<gr_complex> preamble_raw; 

  /**
   * @brief vector containing the preamble upchirps
   *
   */
  std::vector<gr_complex> preamble_up;

  /**
   * @brief number of upchirp symbols to use for CFO and STO frac
  estimation
   *
   */
  int up_symb_to_use;

  /**
   * @brief integer part of CFO+STO
   *
   */
  int k_hat;

  /**
   * @brief fractional part of CFO
   *
   */
  double lambda_cfo;

  /**
   * @brief fractional part of CFO using Berniers algo
   *
   */
  double lambda_bernier;

  /**
   * @brief fractional part of CFO
   *
   */
  double lambda_sto;

  /**
   * @brief indicate that the estimation of lambda_cfo/sto has been
  performed
   *
   */
  bool cfo_sto_est;

  /**
   * @brief upsampling factor used by the FIR interpolator
   *
   */
  int usFactor;

  /**
   * @brief cfo frac correction vector
   *
   */
  std::vector<gr_complex> CFO_frac_correc;

  /**
   * @brief symbol with CFO frac corrected
   *
   */
  std::vector<gr_complex> symb_corr;

  /**
   * @brief value of the preamble downchirps
   *
   */
  int down_val;

  /**
   * @brief integer part of CFO
   *
   */
  int CFOint;

  /**
   * @brief offset of the network identifier
   *
   */
  int net_id_off;

// #ifdef GRLORA_MEASUREMENTS
//   int off_by_one_id; ///< Indicate that the network identifiers where off by one
//                      ///< and corrected
//   std::ofstream sync_log; ///< savefile containing the offset estimation and the
//                           ///< signal strength estimation
//   int numb_symbol_to_save; ///< number of symbol to save for every erroneous
//                            ///< frame
//   std::vector<gr_complex>
//       last_frame; ///< vector storing samples of the last received frame
//   std::ofstream
//       samples_file; ///< savefile containing the samples of the erroneous frames
// #endif

  /**
   * @brief Function that handles the coding rate
   * 
   * @param cr : coding rate
   */
  void header_cr_handler(pmt::pmt_t cr);

  /**
   * @brief Function that handles the payload length (i.e. data length)
   *
   * @param pay_len :payload length
   */
  void header_pay_len_handler(pmt::pmt_t pay_len);

  /**
   * @brief Function to handle the crc of the header
   *
   * @param crc : crc 
   */
  void header_crc_handler(pmt::pmt_t crc);

  /**
   * @brief Handles frame errors coming from the decoding
   *
   * @param err : error message
   */
  void frame_err_handler(pmt::pmt_t err);

  /**
   * @brief Estimate the value of fractional part of the CFO using RCTSL
   *
   * @param samples The pointer to the preamble beginning.(We might want to
   * avoid the first symbol since it might be incomplete)
   */
  void estimate_CFO(gr_complex *samples);

  /**
   * @brief (not used) Estimate the value of fractional part of the CFO using
   * Berniers algorithm
   *
   */
  void estimate_CFO_Bernier();

  /**
   * @brief Estimate the value of fractional part of the STO from m_consec_up
   *
   */
  void estimate_STO();

  /**
   * @brief Function that gets the symbol from the received samples
   *
   * @param samples : the complex samples 
   * @param ref_chirp The reference chirp to use to dechirp the lora symbol.
   * @return uint32_t
   */
  uint32_t get_symbol_val(const gr_complex *samples, gr_complex *ref_chirp);

  /**
   * @brief Determine the energy of a symbol.
   *
   * @param samples The complex symbol to analyse.
   * @return float
   */
  float determine_energy(const gr_complex *samples);

  /**
   * @brief Handles the error message coming from the header decoding.
   *
   * @param err : error message
   */
  void header_err_handler(pmt::pmt_t err);

public:
  /**
   * @brief Construct a new frame sync impl object
   *
   * @param samp_rate : sampling rate
   * @param bandwidth : bandwidth
   * @param sf : spreading factor
   * @param impl_head : boolean to tell if system is in implicit header mode or not
   */
  frame_sync_impl(float samp_rate, uint32_t bandwidth, uint8_t sf,
                  bool impl_head);
  /**
   * @brief Destroy the frame sync impl object
   *
   */
  ~frame_sync_impl();

  /**
   * @brief Standard gnuradio function to tell the system
   * how many input items are needed to produce one output item
   *
   * @param noutput_items : number of output items
   * @param ninput_items_required : number of required input items
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function where the main logic and computation resides.
   * Function will find the window of samples and preform several estimates 
   * to synchronies the internal window of samples to have been received (i.e. align them in time and frequency)
   *
   * @param noutput_items : number of output items
   * @param ninput_items : number of input items
   * @param input_items : input items
   * @param output_items : output items (i.e. start of Rx decoding)
   * @return int
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H */
