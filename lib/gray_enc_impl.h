#ifndef INCLUDED_LORA_GRAY_ENC_IMPL_H
#define INCLUDED_LORA_GRAY_ENC_IMPL_H
// #define GRLORA_DEBUG
#include <lora_sdr/gray_enc.h>


namespace gr {
  namespace lora_sdr {

    class gray_enc_impl : public gray_enc
    {
      public:
      gray_enc_impl( );
      ~gray_enc_impl();

      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_GRAY_ENC_IMPL_H */
