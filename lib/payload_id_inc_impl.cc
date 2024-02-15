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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "payload_id_inc_impl.h"

namespace gr {
  namespace lora_sdr {

    payload_id_inc::sptr
    payload_id_inc::make(std::string separator)
    {
      return gnuradio::get_initial_sptr
        (new payload_id_inc_impl(separator));
    }


    /*
     * The private constructor
     */
    payload_id_inc_impl::payload_id_inc_impl(std::string separator)
      : gr::sync_block("payload_id_inc",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
      m_separator = separator;
      message_port_register_in(pmt::mp("msg_in"));
      message_port_register_out(pmt::mp("msg_out"));
      // set_msg_handler(pmt::mp("noise_est"),boost::bind(&mu_detection_impl::noise_handler, this, _1));
      set_msg_handler(pmt::mp("msg_in"), [this](pmt::pmt_t msg)
                      { this->msg_handler(msg); });
    }

    /*
     * Our virtual destructor.
     */
    payload_id_inc_impl::~payload_id_inc_impl()
    {
    }
    void payload_id_inc_impl::msg_handler(pmt::pmt_t msg)
      {
        // std::cout << "[mu_detection_impl.cc] Noise estimation received: "<<pmt::to_double(noise_est) << '\n';
        std::string in_msg = pmt::symbol_to_string(msg);
        // std::string out_msg = removeNumbers(in_msg);
        std::string out_msg = in_msg.substr(0, in_msg.find(":")+2);
        out_msg = out_msg.append(std::to_string(++m_cnt)); 
        message_port_pub(pmt::intern("msg_out"), pmt::string_to_symbol(out_msg));
      }
    int
    payload_id_inc_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
  
      // Tell runtime system how many output items we produced.
      return 0;
    }

  } /* namespace lora_sdr */
} /* namespace gr */

