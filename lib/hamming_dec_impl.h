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

#ifndef INCLUDED_LORA_hamming_dec_IMPL_H
#define INCLUDED_LORA_hamming_dec_IMPL_H

#include <lora_sdr/hamming_dec.h>

namespace gr {
  namespace lora_sdr {

    class hamming_dec_impl : public hamming_dec
    {
     private:
        uint8_t m_cr;   ///< Transmission coding rate
        uint8_t cr_app; ///< Coding rate use for the block
        bool is_first;  ///< Indicate that it is the first block

        /**
         *  \brief  Handles the coding rate received from the header_decoder block.
         */
        void header_cr_handler(pmt::pmt_t cr);

        /**
         *  \brief  Reset the block variables for a new frame.
         */
        void new_frame_handler(pmt::pmt_t id);

     public:
      hamming_dec_impl( );
      ~hamming_dec_impl();

      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_hamming_dec_IMPL_H */
