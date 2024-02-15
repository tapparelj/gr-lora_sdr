#ifndef INCLUDED_LORA_GRAY_MAPPING_IMPL_H
#define INCLUDED_LORA_GRAY_MAPPING_IMPL_H
// #define GRLORA_DEBUG
#include <gnuradio/lora_sdr/gray_mapping.h>


namespace gr {
  namespace lora_sdr {

    class gray_mapping_impl : public gray_mapping
    {
     private:
      uint8_t m_sf;           ///< Spreading factor
      bool m_soft_decoding;   ///< Hard/Soft decoding

     public:
      gray_mapping_impl(bool soft_decoding);
      ~gray_mapping_impl();

      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_GRAY_MAPPING_IMPL_H */
