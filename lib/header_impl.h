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

#ifndef INCLUDED_LORA_HEADER_IMPL_H
#define INCLUDED_LORA_HEADER_IMPL_H

#include <lora_sdr/header.h>

namespace gr {
  namespace lora_sdr {

    class header_impl : public header
    {
     private:
      bool m_impl_head; ///< indicate if the header is implicit
      bool m_has_crc; ///< indicate the presence of a payload crc
      uint8_t m_cr; ///< Transmission coding rate
      uint8_t m_payload_len; ///< Payload length

      void msg_handler(pmt::pmt_t message);

     public:
      header_impl(bool impl_head, bool has_crc, uint8_t cr);
      ~header_impl();

      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_HEADER_IMPL_H */
