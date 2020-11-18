#ifndef INCLUDED_LORA_HAMMING_ENC_IMPL_H
#define INCLUDED_LORA_HAMMING_ENC_IMPL_H

#include <lora_sdr/hamming_enc.h>

namespace gr {
  namespace lora_sdr {

    class hamming_enc_impl : public hamming_enc
    {
     private:
        uint8_t m_cr; ///< Transmission coding rate
        uint8_t m_sf; ///< Transmission spreading factor

     public:
      hamming_enc_impl(uint8_t cr, uint8_t sf);
      ~hamming_enc_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_HAMMING_ENC_IMPL_H */
