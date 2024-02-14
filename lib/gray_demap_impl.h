#ifndef INCLUDED_LORA_GRAY_DEMAP_IMPL_H
#define INCLUDED_LORA_GRAY_DEMAP_IMPL_H


#include <gnuradio/lora_sdr/gray_demap.h>

namespace gr {
  namespace lora_sdr {

    class gray_demap_impl : public gray_demap
    {
     private:
      uint8_t m_sf;

     public:
      gray_demap_impl(uint8_t sf);
      ~gray_demap_impl();
      void set_sf(uint8_t sf);

      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_GRAY_DEMAP_IMPL_H */
