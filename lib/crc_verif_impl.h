#ifndef INCLUDED_LORA_CRC_VERIF_IMPL_H
#define INCLUDED_LORA_CRC_VERIF_IMPL_H

#include <lora_sdr/crc_verif.h>

namespace gr {
  namespace lora_sdr {

    class crc_verif_impl : public crc_verif
    {
     private:
        uint32_t m_payload_len;///< Payload length in bytes
        bool m_crc_presence;///< Indicate if there is a payload CRC
        uint16_t m_crc;///< The CRC calculated from the received payload
        std::string message_str;///< The payload string
        char m_char;///< A new char of the payload
        bool new_frame; ///<indicate a new frame
        std::vector<uint8_t> in_buff;///< input buffer containing the data bytes and CRC if any

        /**
         * @brief Handles the payload length received from the header_decoder block.
         * 
         * @param payload_len 
         */
        void header_pay_len_handler(pmt::pmt_t payload_len);

        /**
         * @brief Handles the crc_presence received from the header_decoder block.
         * 
         * @param crc_presence 
         */
        void header_crc_handler(pmt::pmt_t crc_presence);

        /**
         * @brief Calculate the CRC 16 using poly=0x1021 and Init=0x0000
         * 
         * @param data : pointer to the data beginning.
         * @param len : length of the data in bytes.
         * @return unsigned int : exit code
         */
        unsigned int crc16(uint8_t* data, uint32_t len);

     public:
      /**
      * @brief Construct a new crc verif impl object
      * 
      */
     
      crc_verif_impl( );
      /**
       * @brief Destroy the crc verif impl object
       * 
       */
      ~crc_verif_impl();

      /**
       * @brief 
       * 
       * @param noutput_items 
       * @param ninput_items_required 
       */
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      /**
       * @brief Main crc verify function that verifies the Cyclic redundancy check (CRC) from the add_crc stage 
       * 
       * @param noutput_items 
       * @param ninput_items 
       * @param input_items 
       * @param output_items 
       * @return int 
       */
      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_CRC_VERIF_IMPL_H */
