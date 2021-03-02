

#ifndef INCLUDED_LORA_WHITENING_IMPL_H
#define INCLUDED_LORA_WHITENING_IMPL_H

#include <lora_sdr/whitening.h>

namespace gr {
  namespace lora_sdr {

    class whitening_impl : public whitening
    {
     private:
         bool new_message; ///< indicate that a new message has to be whitened
         std::vector<uint8_t> m_payload; ///< store the payload bytes
         void msg_handler(pmt::pmt_t message);

     public:
      whitening_impl();
      ~whitening_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_WHITENING_IMPL_H */
