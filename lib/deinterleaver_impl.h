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

#ifndef INCLUDED_LORA_DEINTERLEAVER_IMPL_H
#define INCLUDED_LORA_DEINTERLEAVER_IMPL_H

// #define GRLORA_DEBUG
#include <lora_sdr/deinterleaver.h>

namespace gr {
  namespace lora_sdr {

    class deinterleaver_impl : public deinterleaver
    {
     private:
      uint8_t m_sf;     ///< Transmission Spreading factor
      uint8_t m_cr;     ///< Transmission Coding rate
      uint8_t sf_app;   ///< Spreading factor to use to deinterleave
      uint8_t cw_len;   ///< Length of a codeword
      bool is_first;    ///< Indicate that we need to deinterleave the first block

      /**
       *  \brief  Reset the block variables when a new lora packet needs to be decoded.
      */
      void new_frame_handler(pmt::pmt_t id);
      /**
       *  \brief  Handles the coding rate received from the header_decoder block.
       */
      void header_cr_handler(pmt::pmt_t cr);


     public:
      deinterleaver_impl(uint8_t sf);
      ~deinterleaver_impl();

      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_DEINTERLEAVER_IMPL_H */
