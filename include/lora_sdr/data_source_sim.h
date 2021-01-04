/* -*- c++ -*- */
/* 
 * Copyright 2020 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_LORA_SDR_DATA_SOURCE_SIM_H
#define INCLUDED_LORA_SDR_DATA_SOURCE_SIM_H

#include <lora_sdr/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief Data source that can both generate random strings or static strings, for more information about the implementation visit data_source_impl
     * Main difference from data_source is that this implementation uses an internal uniform distribution, for the timing of the msg pmt channel.
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API data_source_sim : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<data_source_sim> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::data_source.
       *
       * To avoid accidental use of raw pointers, lora_sdr::data_source's
       * constructor is in a private implementation
       * class. lora_sdr::data_source::make is the public interface for
       * creating new instances.
       */
      static sptr make(int pay_len,int n_frames, std::string string_input, uint32_t mean);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_DATA_SOURCE_H */
