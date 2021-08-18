/* -*- c++ -*- */
/*
 * Copyright 2020 Joachim Tapparel TCL@EPFL.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_LORA_SDR_MU_DETECTION_IMPL_H
#define INCLUDED_LORA_SDR_MU_DETECTION_IMPL_H

// #define GRLORA_DEBUG //The output of the downchirps matched filters will be
// saved (including all polyphases) #ifdef THREAD_MEASURE
#include <fstream>
#include <iostream>
#include <lora_sdr/mu_detection.h>
#include "helpers.h"
#include <volk/volk.h>

extern "C" {
#include "kiss_fft.h"
}

namespace gr {
namespace lora_sdr {
struct est_param {

  long sto_int;
  double sto_frac;
  long cfo_int;
  double cfo_frac;
  int s_up;
  int s_down;
  double power;
  double snr;
};

class mu_detection_impl : public mu_detection {
private:
  uint32_t m_bw;                 ///< Bandwidth

  uint8_t m_sf;                  ///< Spreading factor

  uint8_t m_n_up;                ///< number of upchirps in preample

  uint32_t m_samples_per_symbol; ///< Number of samples per lora symbols

  uint32_t m_N;                  ///< 2^sf

  uint8_t m_os_factor;           ///< oversampling factor

  float m_snr_threshold;         ///< minimal SNR to consider a new user


  bool m_init = true; ///< variable used to initialise thread affinity

  float m_prod_max_mag; ///< magnitude of the max bin of the product of the dft
                        ///< of the 7 upchirps
  float m_power_avg;    ///< average of the power of the main bin of the lasts
                     ///< FFTs. Used to avoid false detection caused by payload.

  float m_noise_est; ///< estimation of the noise amplitude

  est_param m_param; ///< parameters estimated s_up, lambda_cfo

  double m_lamda_cfo; ///< estimated CFO fractional part
  std::vector<gr_complex>
      m_deci_preamb_up; ///< decimated part of the preamble that could
                        ///< potentially contain the upchirps
  std::vector<gr_complex> m_downchirp; ///< Reference downchirp
  std::vector<std::vector<gr_complex>>
      m_dfts; ///< vector of the dft of the symbols 1 to 7 in m_preamble
  std::vector<std::vector<float>>
      m_dfts_mag; ///< vector of the dft magnitude of the symbols 1 to 7 in
                  ///< m_preamble
  std::vector<float> m_dft_mag_prod; ///< contain the multiplication of the
                                     ///< n_up-1 upchirps dfts
  bool m_wait_one_symb; ///< variable used to indicate that a new user has been
                        ///< found but that his parameter estimation might not
                        ///< be ideal and a better approx. might come if we wait
                        ///< one additional symbol
  bool m_ignore_next;   ///< variable used to indicate that a new user has been
                        ///< found but it can lead to an additional detection in
                        ///< the next symbol, which might be ignored.

  float m_L_threshold; ///< threshold used to check that we found the wanted
                       ///< pattern in the matched filter output (mf of the 2
                       ///< downchirps)

  std::vector<gr_complex>
      m_preamble; ///< buffer storing the preamble + 2 symbols (7 upchirps, 2
                  ///< net_id and 2 downchirps)
  std::vector<gr_complex>
      m_matched_filter; ///< matched filter for two  downchirps detection
  std::vector<gr_complex>
      m_deci_preamb_down; ///< decimated part of the preamble that could
                          ///< potentially contain downchirps
  std::vector<gr_complex> m_mf_conv_out; ///< output of the convolution of the
                                         ///< preamble end with the match filter
  std::vector<std::vector<float>>
      m_mf_conv_out_abs; ///< the magnitude of m_mf_conv_out

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
   * @brief Estimate the value of fractional part of the CFO using Berniers
   * algorithm
   * 
   * @param delay 
   */
  void estimate_CFO_frac(int delay);

  /**
   * @brief add a tag to the first sample of the newly detected user,
   * containing his power, sto and cfo estimations.
   * 
   * @param input_symb 
   */
  void add_user_tag(int input_symb);

  /**
   * \brief handle message containing the noise estimation.
   */
  void noise_handler(pmt::pmt_t noise_est);

#ifdef GRLORA_DEBUG
  std::ofstream out_file;
  int m_matched_filter_en;
#endif

public:
  /**
   * @brief Construct a new mu detection impl object
   *
   * @param sf
   * @param os_factor
   * @param snr_threshold
   */
  mu_detection_impl(uint8_t sf, uint8_t os_factor, int snr_threshold);
  /**
   * @brief Destroy the mu detection impl object
   *
   */
  ~mu_detection_impl();

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

#endif /* INCLUDED_LORA_SDR_MU_DETECTION_IMPL_H */
