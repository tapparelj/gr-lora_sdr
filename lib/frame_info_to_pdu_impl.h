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

#ifndef INCLUDED_LORA_SDR_FRAME_INFO_TO_PDU_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_INFO_TO_PDU_IMPL_H

#include <gnuradio/lora_sdr/frame_info_to_pdu.h>
#include <vector>

namespace gr {
  namespace lora_sdr {

    class frame_info_to_pdu_impl : public frame_info_to_pdu
    {
     private:
      std::vector<uint8_t> d_buffer;
      long d_expected_len;

     public:
      frame_info_to_pdu_impl();
      ~frame_info_to_pdu_impl();

      int general_work(
              int noutput_items,
              gr_vector_int &ninput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_INFO_TO_PDU_IMPL_H */
