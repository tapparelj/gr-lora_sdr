#ifndef INCLUDED_LORA_SDR_ERR_MEASURES_IMPL_H
#define INCLUDED_LORA_SDR_ERR_MEASURES_IMPL_H

// #define GRLORA_MEASUREMENTS

#include <lora_sdr/err_measures.h>
#include <iostream>
#include <fstream>

namespace gr {
  namespace lora_sdr {

    class err_measures_impl : public err_measures
    {
     private:
        /**
         * @brief Vector containing the reference payload
         * 
         */
        std::vector<char> m_corr_payload; 

        /**
         * @brief Vector containing the received payload
         * 
         */
        std::vector<char> m_payload; 

        /**
         * @brief Bits errors in the frame
         * 
         */
        int BE; 

        /**
         * @brief variable used to detect missing frames
         * 
         */
        int drop; 

        // #ifdef GRLORA_MEASUREMENTS
        // std::ofstream err_outfile;
        // #endif

        /**
         * @brief Msg handler, will handle the incoming decoded message
         * 
         * @param msg : decoded payload message
         */
        void msg_handler(pmt::pmt_t msg);

        /**
         * @brief Reference handler, input of the reference payload
         * 
         * @param ref : reference payload to compare against
         */
        void ref_handler(pmt::pmt_t ref);

     public:
     /**
      * @brief Construct a new err measures impl object
      * 
      */
      err_measures_impl( );
      
      /**
       * @brief Destroy the err measures impl object
       * 
       */
      ~err_measures_impl();

      /**
       * @brief Main function of error measurement
       * 
       * @param noutput_items : number of output items
       * @param input_items  : input items (i.e data from dewhitening)
       * @param output_items : output data (i.e. decode payload)
       * @return int 
       */
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_ERR_MEASURES_IMPL_H */
