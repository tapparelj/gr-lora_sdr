#ifndef INCLUDED_LORA_hamming_dec_IMPL_H
#define INCLUDED_LORA_hamming_dec_IMPL_H

#include <gnuradio/lora_sdr/hamming_dec.h>

namespace gr {
  namespace lora_sdr {

    class hamming_dec_impl : public hamming_dec
    {
     private:        
        uint8_t m_cr;   ///< Transmission coding rate
        uint8_t cr_app; ///< Coding rate use for the block
        bool is_header;  ///< Indicate that it is the first block
        bool m_soft_decoding;   ///< Hard/Soft decoding

     public:
      hamming_dec_impl(bool soft_decoding);
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
