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

#ifndef INCLUDED_LORA_SDR_SIGNAL_DETECTOR_IMPL_H
#define INCLUDED_LORA_SDR_SIGNAL_DETECTOR_IMPL_H

#include <lora_sdr/signal_detector.h>
#include <volk/volk.h>
#include <lora_sdr/utilities.h>
#include <iostream>
#include <fstream>
extern "C"
{
#include "kiss_fft.h"
}

// #define GRLORA_DEBUG //it will save the transparency state along with the decision value
// #define THREAD_MEASURE

namespace gr
{
  namespace lora_sdr
  {

    class signal_detector_impl : public signal_detector
    {
    private:
      uint8_t m_sf;                  ///< Spreading factor
      uint32_t m_samples_per_symbol; ///< Number of samples per LoRa symbol
      uint32_t m_N;                  ///< 2^sf
      uint8_t m_os_factor;           ///< oversampling factor
      double m_threshold;            ///< detection threshold
      int m_fft_symb;                ///< number of symbols on which the fft will be made
      int m_margin;                  ///< margin in the input buffer that will be output when a detection occurs [number of symbols]
      int m_transp_len;              ///< duration (in number of symbol of the transparency after signal detection)

      int transp_duration; ///< duration of transparency left in samples.
      bool first_time_tag; ///< Indicate that a starting tag has been received. Any additional tag will signify an overflow and stop the receiver.

      std::vector<gr_complex> m_downchirp;///< the reference downchirp
      std::vector<gr_complex> m_dechirped;///< the dechirped symbols on which we need to perform the FFT.
      std::vector<gr_complex> cx_out;     ///< the output of the FFT
      kiss_fft_cfg fft_cfg;               ///< the configuration of the FFT

      std::vector<gr_complex> m_input_decim; ///< decimated input 
      std::vector<float>::iterator m_max_it;  ///< iterator used to find max and argmax of FFT
      std::vector<float> m_dfts_mag; ///< vector containing the magnitude of the FFT.

#ifdef GRLORA_DEBUG
      std::ofstream out_file;
#endif
#ifdef THREAD_MEASURE
      bool m_init; ///< variable use to set thread priority
#endif

    public:
    /**
     * @brief Construct a new signal detector impl object
     * 
     * @param sf 
     * @param os_factor 
     * @param threshold 
     * @param margin 
     * @param fft_symb 
     * @param transp_len 
     */
      signal_detector_impl(uint8_t sf, uint8_t os_factor, double threshold, int margin, int fft_symb, int transp_len);
      /**
       * @brief Destroy the signal detector impl object
       * 
       */
      ~signal_detector_impl();

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
      int general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_SIGNAL_DETECTOR_IMPL_H */
