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

#ifndef INCLUDED_LORA_MODULATE_IMPL_H
#define INCLUDED_LORA_MODULATE_IMPL_H

#include <lora_sdr/modulate.h>
#include <gnuradio/io_signature.h>
#include <iostream>
#include <fstream>

#include <lora_sdr/utilities.h>

namespace gr {
  namespace lora_sdr {

    class modulate_impl : public modulate
    {
     private:
       uint8_t m_sf; ///< Transmission spreading factor
       uint32_t m_samp_rate; ///< Transmission sampling rate
       uint32_t m_bw; ///< Transmission bandwidth (Works only for samp_rate=bw)
       uint32_t m_number_of_bins; ///< number of bin per loar symbol
       double m_symbols_per_second; ///< lora symbols per second
       uint32_t m_samples_per_symbol; ///< samples per symbols(Works only for 2^sf)

       std::vector<gr_complex> m_upchirp; ///< reference upchirp
       std::vector<gr_complex> m_downchirp; ///< reference downchirp

       uint n_up; ///< number of upchirps in the preamble
       uint32_t symb_cnt; ///< counter of the number of lora symbols sent

       void msg_handler(pmt::pmt_t message);

     public:
      modulate_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw);
      ~modulate_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_MODULATE_IMPL_H */
