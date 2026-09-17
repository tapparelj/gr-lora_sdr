/* -*- c++ -*- */
/*
 * Copyright 2026 Justin Garey & Zach Naymik.
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

#ifndef INCLUDED_LORA_SDR_FRAME_INFO_TO_PDU_H
#define INCLUDED_LORA_SDR_FRAME_INFO_TO_PDU_H

#include <gnuradio/lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief Frame Info to PDU. Segments a tagged byte stream into PDUs
     * using the pay_len field of the 'frame_info' tag, combining what the
     * frame_info to packet_len and tagged stream to PDU blocks did separately.
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API frame_info_to_pdu : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<frame_info_to_pdu> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::frame_info_to_pdu.
       *
       * To avoid accidental use of raw pointers, lora_sdr::frame_info_to_pdu's
       * constructor is in a private implementation
       * class. lora_sdr::frame_info_to_pdu::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_INFO_TO_PDU_H */
