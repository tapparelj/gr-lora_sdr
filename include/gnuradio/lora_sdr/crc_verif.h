/* -*- c++ -*- */
/* 
 * Copyright 2022 Tapparel Joachim @EPFL,TCL.
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


#ifndef INCLUDED_LORA_SDR_CRC_VERIF_H
#define INCLUDED_LORA_SDR_CRC_VERIF_H

#include <gnuradio/lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief <+description of block+>
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API crc_verif : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<crc_verif> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::crc_verif.
       *
       * To avoid accidental use of raw pointers, lora_sdr::crc_verif's
       * constructor is in a private implementation
       * class. lora_sdr::crc_verif::make is the public interface for
       * creating new instances.
       */
      static sptr make(bool print_rx_msg, bool output_crc_check);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_CRC_VERIF_H */

