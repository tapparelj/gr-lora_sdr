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
#ifndef INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H
#define INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H

#include <lora_sdr/data_source.h>
#include <lora_sdr/utilities.h>

namespace gr {
  namespace lora_sdr {

    class data_source_impl : public data_source
    {
     private:
         int frame_cnt; ///< count the number of frame sent
         int m_n_frames;///< The maximal number of frame to send
         int m_pay_len; ///< The payload length

         /**
          *  \brief  return a random string containing [a-z A-Z 0-9]
          *
          *  \param  nbytes
          *          The number of char in the string
          */
         std::string random_string(int nbytes);
         /**
          *  \brief  Handles trigger messages
          */
         void trigg_handler(pmt::pmt_t id);

     public:
      data_source_impl(int pay_len,int n_frames);
      ~data_source_impl();

      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };
  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H */
