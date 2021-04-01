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


#ifndef INCLUDED_LORA_SDR_MU_DETECTION_H
#define INCLUDED_LORA_SDR_MU_DETECTION_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * 
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API mu_detection : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<mu_detection> sptr;

      /*!
       * \brief New user detection and parameters estimations
       * 
       *  This block is responsible for the user detection and parameter estimation. On a successful user detection, a tag containing the estimations of the user
       * power, cfo and sto is attached to the first sample containing the new user signal. 
       * 
       * \param sf Spreading factor
       * \param os_factor Oversampling factor
       * \param snr_threshold Mininal SNR required to validate a triggered new user detection.
       */
      static sptr make(uint8_t sf, uint8_t os_factor, int snr_threshold);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_MU_DETECTION_H */

