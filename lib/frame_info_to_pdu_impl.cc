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
#include "frame_info_to_pdu_impl.h"

namespace gr {
  namespace lora_sdr {

    frame_info_to_pdu::sptr
    frame_info_to_pdu::make()
    {
      return gnuradio::get_initial_sptr
        (new frame_info_to_pdu_impl());
    }

    /*
     * The private constructor
     */
    frame_info_to_pdu_impl::frame_info_to_pdu_impl()
      : gr::block("frame_info_to_pdu",
              gr::io_signature::make(1, 1, sizeof(uint8_t)),
              gr::io_signature::make(0, 0, 0)),
        d_expected_len(-1)
    {
      message_port_register_out(pmt::mp("pdus"));
    }

    /*
     * Our virtual destructor.
     */
    frame_info_to_pdu_impl::~frame_info_to_pdu_impl()
    {
    }

    int
    frame_info_to_pdu_impl::general_work(int noutput_items,
        gr_vector_int &ninput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const uint8_t *in = (const uint8_t *)input_items[0];
      int n = ninput_items[0];

      // the pay_len field of the frame_info tag marks the length of the next payload
      std::vector<tag_t> tags;
      get_tags_in_window(tags, 0, 0, n, pmt::intern("frame_info"));
      for (const tag_t &tag : tags) {
        long pay_len = pmt::to_long(pmt::dict_ref(tag.value, pmt::intern("pay_len"), pmt::from_long(-1)));
        if (pay_len > 0) {
          d_expected_len = pay_len;
        }
      }

      d_buffer.insert(d_buffer.end(), in, in + n);
      consume_each(n);

      if (d_expected_len > 0 && (long)d_buffer.size() >= d_expected_len) {
        pmt::pmt_t vec = pmt::init_u8vector(d_expected_len, d_buffer.data());
        message_port_pub(pmt::mp("pdus"), pmt::cons(pmt::PMT_NIL, vec));
        d_buffer.erase(d_buffer.begin(), d_buffer.begin() + d_expected_len);
        d_expected_len = -1;
      }

      return 0;
    }

  } /* namespace lora_sdr */
} /* namespace gr */
