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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "RH_RF95_header_impl.h"

namespace gr {
  namespace lora_sdr {

    RH_RF95_header::sptr
    RH_RF95_header::make(uint8_t _to, uint8_t _from, uint8_t _id, uint8_t _flags)
    {
      return gnuradio::get_initial_sptr
        (new RH_RF95_header_impl(_to, _from, _id, _flags));
    }

    /*
     * The private constructor
     */
    RH_RF95_header_impl::RH_RF95_header_impl(uint8_t _to, uint8_t _from, uint8_t _id, uint8_t _flags)
      : gr::block("RH_RF95_header",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
      {
            m_to = _to;
            m_from = _from;
            m_id = _id;
            m_flags = _flags;

            message_port_register_out(pmt::mp("msg"));
            message_port_register_in(pmt::mp("msg"));
            set_msg_handler(pmt::mp("msg"), boost::bind(&RH_RF95_header_impl::msg_handler, this, _1));
      }
  /*
     * Our virtual destructor.
     */
    RH_RF95_header_impl::~RH_RF95_header_impl()
    {}

    void
    RH_RF95_header_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {}
    void RH_RF95_header_impl::msg_handler(pmt::pmt_t message){
     std::string str=pmt::symbol_to_string(message);
     std::string s({ m_to,m_from,m_id,m_flags });
     str=s+str;
     message_port_pub(pmt::intern("msg"),pmt::mp(str));
  }

    int
    RH_RF95_header_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      std::cout<<"there"<<std::endl;
      // Tell runtime system how many output items we produced.
      return 0;
    }
  } /* namespace lora_sdr */
} /* namespace gr */
