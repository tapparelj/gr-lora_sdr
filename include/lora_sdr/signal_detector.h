/* -*- c++ -*- */
/* 
 * Copyright 2020 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_LORA_SDR_SIGNAL_DETECTOR_H
#define INCLUDED_LORA_SDR_SIGNAL_DETECTOR_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * 
     * \ingroup lora_sdr
     * 
     */
    class LORA_SDR_API signal_detector : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<signal_detector> sptr;
  
      /*!
       * \brief This block becomes transparent after detecting a LoRa preamble at his input.
       * 
       * It's main purpose is to prevent the rest of the receiver to run continuously as the matched filtering steps are computationally intensive.
       * The detection of a LoRa preamble is based on the FFT of 'fft_symb' dechirped symbols. If 'fft_symb' upchirps are in the FFT, a bin should have significantly more energy than others. 
       * The decision is taken based on the ratio between the amplitude of the main bin and the median amplitude of all bins.
       * Once a detection is triggered, the block will become transparent for the previous 'margin' symbols and the next 'transp_len' symbols. 
       * The transparency duration is reset if a new trigger occurs before the end of the previous tranparency duration.
       * 
       * \param sf Spreading factor
       * \param os_factor Oversampling factor
       * \param threshold Minimal ratio between the max FFT bin and the median of the bins.(a value of 10 has proven to be effective)
       * \param margin Number of symbols preceding the detection that will be output at the detection time. (margin in case of detection triggering late on the preamble)
       * \param fft_symb Number of symbols used in the FFT (should be less than the number of preamble upchirps, 4 is an efficient value for the FFT complexity)
       * \param transp_len minimal duration in symbols after a triggered detection (englobing the preamble and payload symbol is a good idea)
       */
      static sptr make(uint8_t sf, uint8_t os_factor, double threshold, int margin, int fft_symb, int transp_len);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_SIGNAL_DETECTOR_H */

