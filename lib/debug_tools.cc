#include <gnuradio/io_signature.h>

namespace gr {
  namespace lora_sdr {
    
    int vector_unit82string(uint8_t input[],int length){
        int count = 0;
        for(int i=0; i < length; i++){
          count++;
        }
        return count;
    }

    int test(){
      return 10;
    }

  } /* namespace lora_sdr */
} /* namespace gr */

