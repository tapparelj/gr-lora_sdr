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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "pdu_to_whitening_msg_impl.h"
#include <iomanip>
#include <sstream>

namespace gr {
  namespace lora_sdr {

    pdu_to_whitening_msg::sptr
    pdu_to_whitening_msg::make()
    {
      return gnuradio::get_initial_sptr
        (new pdu_to_whitening_msg_impl());
    }

    /*
     * The private constructor
     */
    pdu_to_whitening_msg_impl::pdu_to_whitening_msg_impl()
      : gr::block("pdu_to_whitening_msg",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
      message_port_register_in(pmt::mp("pdus"));
      message_port_register_out(pmt::mp("msg"));
      set_msg_handler(pmt::mp("pdus"), [this](pmt::pmt_t msg) { this->msg_handler(msg); });
    }

    /*
     * Our virtual destructor.
     */
    pdu_to_whitening_msg_impl::~pdu_to_whitening_msg_impl()
    {
    }

    // Converts TUN PDUs to whitening message input.
    void
    pdu_to_whitening_msg_impl::msg_handler(pmt::pmt_t pdu)
    {
      if (!pmt::is_pair(pdu)) {
        return;
      }
      pmt::pmt_t vec = pmt::cdr(pdu);
      if (!pmt::is_u8vector(vec)) {
        return;
      }
      std::vector<uint8_t> data = pmt::u8vector_elements(vec);
      std::stringstream hex_stream;
      hex_stream << std::hex << std::setfill('0');
      for (uint8_t byte : data) {
        hex_stream << std::setw(2) << static_cast<int>(byte);
      }
      message_port_pub(pmt::intern("msg"), pmt::intern(hex_stream.str()));
    }

    int
    pdu_to_whitening_msg_impl::general_work(int noutput_items,
        gr_vector_int &ninput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      // Tell runtime system how many output items we produced.
      return 0;
    }

  } /* namespace lora_sdr */
} /* namespace gr */
