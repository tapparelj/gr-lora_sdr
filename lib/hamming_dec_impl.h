#ifndef INCLUDED_LORA_hamming_dec_IMPL_H
#define INCLUDED_LORA_hamming_dec_IMPL_H

#include <lora_sdr/hamming_dec.h>

namespace gr {
  namespace lora_sdr {

    class hamming_dec_impl : public hamming_dec
    {
     private:
        uint8_t m_cr;   ///< Transmission coding rate
        uint8_t cr_app; ///< Coding rate use for the block
        bool is_first;  ///< Indicate that it is the first block

        /**
         *  \brief  Handles the coding rate received from the header_decoder block.
         */
        void header_cr_handler(pmt::pmt_t cr);

        /**
         *  \brief  Reset the block variables for a new frame.
         */
        void new_frame_handler(pmt::pmt_t id);

     public:
      hamming_dec_impl( );
      ~hamming_dec_impl();

      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_hamming_dec_IMPL_H */
