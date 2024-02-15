/* -*- c++ -*- */
/*
 *     This file is part of gr-lora_sdr.
 *
 *     This program is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU General Public License as published by
 *     the Free Software Foundation, either version 3 of the License, or
 *     (at your option) any later version.
 *
 *     This program is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU General Public License for more details.
 *
 *     You should have received a copy of the GNU General Public License
 *     along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef INCLUDED_LORA_SDR_MSG_SINK_IMPL_H
#define INCLUDED_LORA_SDR_MSG_SINK_IMPL_H

#include <gnuradio/lora_sdr/msg_sink.h>
#include <fstream>

namespace gr {
  namespace lora_sdr {

class msg_sink_impl : public msg_sink
{
private:
    std::ofstream d_output_file;
    // Nothing to declare in this block.

public:
    msg_sink_impl(const std::string &filename);
    ~msg_sink_impl();

    // Where all the action really happens
    //void forecast(int noutput_items, gr_vector_int& ninput_items_required);
    /*
    int general_work(int noutput_items,
                     gr_vector_int& ninput_items,
                     gr_vector_const_void_star& input_items,
                     gr_vector_void_star& output_items);
                     */

    
    void process_msg(pmt::pmt_t hex_msg);
    
};

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_MSG_SINK_IMPL_H */
