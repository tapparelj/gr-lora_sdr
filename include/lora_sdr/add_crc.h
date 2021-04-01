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


#ifndef INCLUDED_LORA_SDR_ADD_CRC_H
#define INCLUDED_LORA_SDR_ADD_CRC_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief <+description of block+>
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API add_crc : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<add_crc> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::add_crc.
       *
       * To avoid accidental use of raw pointers, lora_sdr::add_crc's
       * constructor is in a private implementation
       * class. lora_sdr::add_crc::make is the public interface for
       * creating new instances.
       */
      static sptr make(bool has_crc);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_ADD_CRC_H */

