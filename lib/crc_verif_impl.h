#ifndef INCLUDED_LORA_CRC_VERIF_IMPL_H
#define INCLUDED_LORA_CRC_VERIF_IMPL_H

#include <gnuradio/lora_sdr/crc_verif.h>

// #define GRLORA_DEBUG

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
        bool print_rx_msg;  ///< print received message in terminal or not
        bool output_crc_check; ///< output the result of the payload CRC check
        tag_t curent_tag; ///< the most recent tag for the packet we are currently processing
        

        uint32_t cnt=0;///< count the number of frame

        /**
         *  \brief  Handles the payload length received from the header_decoder block.
         */
        void header_pay_len_handler(pmt::pmt_t payload_len);
        /**
         *  \brief  Handles the crc_presence received from the header_decoder block.
         */
        void header_crc_handler(pmt::pmt_t crc_presence);
        /**
         *  \brief  Calculate the CRC 16 using poly=0x1021 and Init=0x0000
         *
         *  \param  data
         *          The pointer to the data beginning.
         *  \param  len
         *          The length of the data in bytes.
         */
        unsigned int crc16(uint8_t* data, uint32_t len);

     public:
      crc_verif_impl(bool print_rx_msg, bool output_crc_check);
      ~crc_verif_impl();

      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_CRC_VERIF_IMPL_H */
