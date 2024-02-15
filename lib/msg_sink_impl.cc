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

#include <gnuradio/io_signature.h>
#include "msg_sink_impl.h"
#include <stdio.h>
#include <chrono>
#include <iomanip>

namespace gr {
  namespace lora_sdr {


	msg_sink::sptr 
	msg_sink::make(const std::string &filename) 
	{ 
		return gnuradio::get_initial_sptr(new msg_sink_impl(filename)); 
	}


/*
 * The private constructor
 */
	msg_sink_impl::msg_sink_impl(const std::string &filename)
	: gr::block("msg_sink",
	                gr::io_signature::make(0, 0, 0),
	              gr::io_signature::make(0, 0, 0)),
	              d_output_file(filename.c_str(),  std::ofstream::binary | std::ofstream::app)
	{
	    if (!d_output_file.is_open()) {
	        // File doesn't exist, create it
	        std::ofstream newFile(filename.c_str());
	        
	        if (d_output_file.is_open()) {
	            std::cout << "File created: " << filename << std::endl;
	            // Optionally, you can write something to the file here
	        } else {
	            std::cerr << "Error creating file: " << filename << std::endl;
	        }
	    } else {
	        std::cout << "File already exists: " << filename << std::endl;
	    }
	    
	    message_port_register_in(pmt::mp("msg_in"));
	    set_msg_handler(pmt::mp("msg_in"), boost::bind(&msg_sink_impl::process_msg, this, boost::placeholders::_1));


	    
	}

	/*
	 * Our virtual destructor.
	 */
	msg_sink_impl::~msg_sink_impl() {
	    if (d_output_file.is_open())
	        {
	            d_output_file.close();
	        }
	}


	std::string getDateTime() {
	    auto now = std::chrono::system_clock::now();
	    std::time_t now_c = std::chrono::system_clock::to_time_t(now);
	    std::tm* localTime = std::localtime(&now_c);

	    std::ostringstream oss;
	    oss << std::put_time(localTime, "%d%m%Y_%H%M%S");
	    return oss.str();
	}



	void msg_sink_impl::process_msg(pmt::pmt_t msg)
	    {
	        
	        //std::string s = pmt::serialize_str(hex_msg);
	        //const char *serialized = s.data();
	        //d_output_file.write(serialized, s.length());

	        //std::string hexResult = asciiToHex(s);
	        std::string timestamp = getDateTime();
	        //std::string filename = "output_" + timestamp + ".txt";
	        //writeHexToFile(filename, s);

	        std::stringstream ss;
	        ss << timestamp << ",";
	        //std::string s = pmt::serialize_str(hex_msg);
	        //std::cout<<hex_msg;
	        //const char *serialized = s.data();
	        ss<<msg<<std::endl;
	        //std::string new_entry;
	        //new_entry = ss.str();
	       	d_output_file<<ss.str();
	        //const char *serialized = s.data();
	        //d_output_file.write(serialized, s.length());


	    }
} /* namespace lora_sdr */
} /* namespace gr */
