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


#ifndef INCLUDED_LORA_SDR_PARTIAL_ML_H
#define INCLUDED_LORA_SDR_PARTIAL_ML_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * 
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API partial_ml : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<partial_ml> sptr;

      /*!
       * \brief Calculate the likelihood of the synchronised user symbol as well as the matched filter output of the two overlapping symbols of the non-synchronised user.
       * 
       * This block evaluate one candidate for Su, returning it's likelihood alongside the two matched filter outputs for the non-synchronized user symbols.
       * The candidate is selected based on the fft of the input window. The 'Id' highest bin will be considered as candidate. 
       * 
       * \param sf Spreading factor
       * \param id ID of the block. Used to indicate the candidate for Su that this block should evaluate.(Should different for each partial_ml block, starting from 0)
       */
      static sptr make(uint8_t sf, uint8_t id);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_PARTIAL_ML_H */

