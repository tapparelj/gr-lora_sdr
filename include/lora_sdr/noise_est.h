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


#ifndef INCLUDED_LORA_SDR_NOISE_EST_H
#define INCLUDED_LORA_SDR_NOISE_EST_H

#include <lora_sdr/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * 
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API noise_est : virtual public gr::sync_block
    {
     public:
      typedef std::shared_ptr<noise_est> sptr;

      /*!
       * \brief This block estimate the noise power using the 'n_samples' first sample presented at his input.
       * 
       * The estimated power is published as a message on his 'noise_est' port
       * 
       * \param n_samples number of samples used to estimate noise
       */
      static sptr make(uint32_t n_samples);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_NOISE_EST_H */

