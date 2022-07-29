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

#ifndef INCLUDED_LORA_SDR_PAYLOAD_ID_INC_IMPL_H
#define INCLUDED_LORA_SDR_PAYLOAD_ID_INC_IMPL_H

#include <gnuradio/lora_sdr/payload_id_inc.h>

namespace gr {
  namespace lora_sdr {

    class payload_id_inc_impl : public payload_id_inc
    {
     private:
      std::string m_separator;
      void msg_handler(pmt::pmt_t msg);
      int m_cnt=0;

     public:
      payload_id_inc_impl(std::string separator);
      ~payload_id_inc_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_PAYLOAD_ID_INC_IMPL_H */

