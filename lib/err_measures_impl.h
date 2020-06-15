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

#ifndef INCLUDED_LORA_SDR_ERR_MEASURES_IMPL_H
#define INCLUDED_LORA_SDR_ERR_MEASURES_IMPL_H

// #define GRLORA_MEASUREMENTS

#include <lora_sdr/err_measures.h>
#include <iostream>
#include <fstream>

namespace gr {
  namespace lora_sdr {

    class err_measures_impl : public err_measures
    {
     private:
        std::vector<char> m_corr_payload; ///< Vector containing the reference payload
        std::vector<char> m_payload; ///< Vector containing the received payload
        int BE; ///< Bits errors in the frame
        int drop; ///< variable used to detect missing frames
        #ifdef GRLORA_MEASUREMENTS
        std::ofstream err_outfile;
        #endif

        void msg_handler(pmt::pmt_t msg);
        void ref_handler(pmt::pmt_t ref);

     public:
      err_measures_impl( );
      ~err_measures_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_ERR_MEASURES_IMPL_H */
