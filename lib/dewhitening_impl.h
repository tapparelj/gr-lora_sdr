/* -*- c++ -*- */
/* 
 * Copyright 2019 Joachim Tapparel TCL@EPFL.
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

#ifndef INCLUDED_LORA_DEWHITENING_IMPL_H
#define INCLUDED_LORA_DEWHITENING_IMPL_H

// #define GRLORA_DEBUG
#include <lora_sdr/dewhitening.h>

namespace gr {
  namespace lora_sdr {

    class dewhitening_impl : public dewhitening
    {
     private:
        int m_payload_len;  ///< Payload length in bytes
        int m_crc_presence; ///< indicate the precence of a CRC
        int offset = 0;       ///< The offset in the whitening table
        std::vector<uint8_t> dewhitened; ///< The dewhitened bytes

        /**
         *  \brief  Handles the payload length received from the header_decoder block.
         */
        void header_pay_len_handler(pmt::pmt_t payload_len);

        /**
         *  \brief  Reset the block variables for a new frame.
         */
        void new_frame_handler(pmt::pmt_t id);
        /**
         *  \brief  Receive indication on the CRC presence
         */
        void header_crc_handler(pmt::pmt_t crc_presence);

     public:
      dewhitening_impl();
      ~dewhitening_impl();

      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_DEWHITENING_IMPL_H */
