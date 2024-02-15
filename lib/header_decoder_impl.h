
#ifndef INCLUDED_LORA_HEADER_DECODER_IMPL_H
#define INCLUDED_LORA_HEADER_DECODER_IMPL_H

#include <gnuradio/lora_sdr/header_decoder.h>
#include <gnuradio/lora_sdr/utilities.h>

namespace gr {
  namespace lora_sdr {

    class header_decoder_impl : public header_decoder
    {
     private:
        const uint8_t header_len = 5; ///< size of the header in nibbles

        bool m_impl_header;///< Specify if we use an explicit or implicit header
        bool m_print_header; ///< print or not header information in terminal
        uint8_t m_payload_len;///< The payload length in bytes
        bool m_has_crc;///< Specify the usage of a payload CRC
        uint8_t m_cr;///< Coding rate
        uint8_t m_ldro_mode; ///< use low datarate optimisation 

        uint8_t header_chk; ///< The header checksum received in the header

        uint32_t pay_cnt;///< The number of payload nibbles received
        uint32_t nout;///< The number of data nibbles to output
        bool is_header ;///< Indicate that we need to decode the header

        /**
         *  \brief  Reset the block variables for a new frame.
         */
        void new_frame_handler();
        /**
         *  \brief publish decoding information contained in the header or provided to the block   
         */
        void publish_frame_info(int cr, int pay_len, int crc, uint8_t ldro, int err);

     public:
      header_decoder_impl(bool impl_head, uint8_t cr, uint32_t pay_len, bool has_crc, uint8_t ldro_mode, bool print_header);
      ~header_decoder_impl();

      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_HEADER_DECODER_IMPL_H */
