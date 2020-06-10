#ifndef INCLUDED_LORA_DEINTERLEAVER_IMPL_H
#define INCLUDED_LORA_DEINTERLEAVER_IMPL_H

// #define GRLORA_DEBUG
#include <lora_sdr/deinterleaver.h>

namespace gr {
  namespace lora_sdr {

    class deinterleaver_impl : public deinterleaver
    {
     private:
      uint8_t m_sf;     ///< Transmission Spreading factor
      uint8_t m_cr;     ///< Transmission Coding rate
      uint8_t sf_app;   ///< Spreading factor to use to deinterleave
      uint8_t cw_len;   ///< Length of a codeword
      bool is_first;    ///< Indicate that we need to deinterleave the first block

      /**
       *  \brief  Reset the block variables when a new lora packet needs to be decoded.
      */
      void new_frame_handler(pmt::pmt_t id);
      /**
       *  \brief  Handles the coding rate received from the header_decoder block.
       */
      void header_cr_handler(pmt::pmt_t cr);


     public:
      deinterleaver_impl(uint8_t sf);
      ~deinterleaver_impl();

      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_DEINTERLEAVER_IMPL_H */
