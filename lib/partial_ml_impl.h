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

#ifndef INCLUDED_LORA_SDR_PARTIAL_ML_IMPL_H
#define INCLUDED_LORA_SDR_PARTIAL_ML_IMPL_H

#include <lora_sdr/partial_ml.h>
#include <volk/volk.h>
#include <lora_sdr/utilities.h>
#include <iostream>
#include <fstream>

extern "C"
{
#include "kiss_fft.h"
}
// #define GRLORA_DEBUG

namespace gr
{
  namespace lora_sdr
  {

    class partial_ml_impl : public partial_ml
    {
    private:
      struct window
      {
        double power1;
        double power2;
        long win_len;
        long Tu;
        long Ti1;
        long Ti2;
        double tau;
        double delta_cfo;
      };
      uint8_t m_sf;        ///< Spreading factor
      uint32_t m_N;        ///< 2^sf
      uint8_t m_os_factor; ///< oversampling factor
      uint8_t m_id;        ///< bloc index
      int m_Ki;            ///< number of bin considered for Si

      window window; ///< the window to process
      bool m_init;   ///< variable used to attach each partial ml block to a different thread

      std::vector<gr_complex> m_ref_upchirp;
      std::vector<gr_complex> m_ref_downchirp;

      std::vector<gr_complex> mf; ///< matched filter
      std::vector<bool> third_symbol_part; ///< variable used to handle the symbol of the non-synchronized user that is cut in three parts (because of the quarter downchirp of the synchronized user).

      int Su; ///< symbol of the synchronized user
      double theta_u; ///< phase estimation of the user u (based on the phase of the bin of maximum amplitude)
      double Mu; ///< magnitude of the bin with index Su
      double SNR_est;///<estimate of the SNR of the preamble of the first user

      //---------- coherent demod--------------
      std::vector<gr_complex> preamb_peak; ///< NOT USED

      double prev_theta_u;
      bool first_upchirp;

      // dechirp the symbol and return the magnitude, the angle and the  the fft
      std::vector<std::tuple<int, double, double>> dechirp_and_fft(const gr_complex *samples, Symbol_type type);

      gr_complex matched_filter1(const gr_complex *dechirped, int win_len, int Si, double tau, double delta_cfo, int win_type);

      gr_complex matched_filter2(const gr_complex *dechirped, int win_len, int Si, double tau, double delta_cfo, int win_type);

      void add_demod_tag(int Su, int Si1, int Si2, double Mu, double Mi1, double Mi2, double SNR_est);

      bool is_kind_upchirp(long t);

      bool is_kind_downchirp(long t);

#ifdef GRLORA_DEBUG
      std::ofstream out_file;
#endif

    public:
      partial_ml_impl(uint8_t sf, uint8_t id);
      ~partial_ml_impl();

      // Where all the action really happens
      void forecast(int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_PARTIAL_ML_IMPL_H */
