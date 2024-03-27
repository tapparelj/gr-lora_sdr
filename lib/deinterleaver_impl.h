#ifndef INCLUDED_LORA_DEINTERLEAVER_IMPL_H
#define INCLUDED_LORA_DEINTERLEAVER_IMPL_H

// #define GRLORA_DEBUG
#include <gnuradio/lora_sdr/deinterleaver.h>

namespace gr {
  namespace lora_sdr {

    class deinterleaver_impl : public deinterleaver
    {
     private:      
      uint8_t m_sf;     ///< Transmission Spreading factor
      uint8_t m_cr;     ///< Transmission Coding rate
      uint8_t sf_app;   ///< Spreading factor to use to deinterleave
      uint8_t cw_len;   ///< Length of a codeword
      bool m_is_header;    ///< Indicate that we need to deinterleave the first block with the default header parameters (cr=4/8, reduced rate)
      bool m_soft_decoding;   ///< Hard/Soft decoding
      bool m_ldro; ///< use low datarate optimization mode
      bool m_legacy_sf56;                 ///< use of legacy SF5/6 mode of sx127x

     public:
      deinterleaver_impl(bool soft_decoding, bool legacy_sf56);
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
