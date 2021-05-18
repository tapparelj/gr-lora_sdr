#include <gnuradio/io_signature.h>
#include "helpers.h"
#include <iostream>

namespace gr {
  namespace lora_sdr {
        /** Turns an gr_complex data type array into an string.
         * To be used for debugging
         *
         * @param input : gr_complex vector
         * @param length : length of the vector
         * @return : string to be used in debugging output
         */
      std::string complex_vector_2_string(gr_complex *input, int length){
          std::string str;
          std::string str_add;
          for(int i=0; i <length; i++){
              str_add = "("+std::to_string(input[i].real()) +"+"+ std::to_string(input[i].imag()) +"j),";
              str.append(str_add);
          }
          return str;
      }

  } /* namespace lora_sdr */
} /* namespace gr */

