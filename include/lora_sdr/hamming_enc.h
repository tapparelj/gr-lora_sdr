/* -*- c++ -*- */
/* 
 * Copyright 2019 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_LORA_SDR_HAMMING_ENC_H
#define INCLUDED_LORA_SDR_HAMMING_ENC_H

#include <lora_sdr/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief Add hamming code to the to be sent playload.
     * This means extra party bits are added to the payload to be able to recover from bit errors during transmission
     * For more information about the implementation visit hamming_enc_impl
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API hamming_enc : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<hamming_enc> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::hamming_enc.
       *
       * To avoid accidental use of raw pointers, lora_sdr::hamming_enc's
       * constructor is in a private implementation
       * class. lora_sdr::hamming_enc::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint8_t cr, uint8_t sf);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_HAMMING_ENC_H */

