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
#include "err_measures_impl.h"

namespace gr {
  namespace lora_sdr {

    err_measures::sptr
    err_measures::make( )
    {
      return gnuradio::get_initial_sptr
        (new err_measures_impl());
    }

    /*
     * The private constructor
     */
    err_measures_impl::err_measures_impl( )
        : gr::sync_block("err_measures",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
        {
        drop = 0;
        message_port_register_in(pmt::mp("msg"));
        set_msg_handler(pmt::mp("msg"), boost::bind(&err_measures_impl::msg_handler, this, _1));
        message_port_register_in(pmt::mp("ref"));
        set_msg_handler(pmt::mp("ref"), boost::bind(&err_measures_impl::ref_handler, this, _1));
        message_port_register_out(pmt::mp("err"));
        #ifdef GRLORA_MEASUREMENTS
        int num = 0;//check next file name to use
        while(1){
            std::ifstream infile("../matlab/measurements/err"+std::to_string(num)+".txt");
             if(!infile.good())
                break;
            num++;
        }
        err_outfile.open("../matlab/measurements/err"+std::to_string(num)+".txt", std::ios::out | std::ios::trunc );
        #endif
        }
    /*
     * Our virtual destructor.
     */
    err_measures_impl::~err_measures_impl()
    {}
        int countSetBits(int n)
  {
      // base case
      if (n == 0)
          return 0;
      else
          return 1 + countSetBits(n & (n - 1));
  }
  void err_measures_impl::msg_handler(pmt::pmt_t msg){
      std::string payload = pmt::symbol_to_string(msg);
      m_payload.resize(payload.length()+1);
      strcpy(&m_payload[0],pmt::symbol_to_string(msg).c_str());
      BE = 0;

      for (size_t i = 0; (i < payload.length())&&(i < m_corr_payload.size()); i++) {
          BE += countSetBits((m_corr_payload[i]^m_payload[i]));
      }
      #ifdef GRLORA_MEASUREMENTS
      err_outfile<<BE<<",";
      #endif
      std::cout << "Error count= "<<BE << '\n';
      if(BE>0)
          message_port_pub(pmt::intern("err"),pmt::mp(true));
      drop=0;
  };
  void err_measures_impl::ref_handler(pmt::pmt_t ref){
      #ifdef GRLORA_MEASUREMENTS
      if(drop){
              err_outfile<<"-1,";
      }
      #endif
      drop=1;
      m_corr_payload.resize(pmt::symbol_to_string(ref).length()+1);
      strcpy(&m_corr_payload[0],pmt::symbol_to_string(ref).c_str());
  }

  int err_measures_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      return 0;
    }

  } /* namespace lora_sdr */
} /* namespace gr */
