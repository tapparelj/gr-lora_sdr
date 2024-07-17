#ifndef INCLUDED_LORA_INTERLEAVER_IMPL_H
#define INCLUDED_LORA_INTERLEAVER_IMPL_H

#include <gnuradio/lora_sdr/interleaver.h>
// #define GRLORA_DEBUG

namespace gr {
  namespace lora_sdr {

    class interleaver_impl : public interleaver
    {
     private:
        uint8_t m_cr; ///< Transmission coding rate
        uint8_t m_sf; ///< Transmission spreading factor

        uint32_t cw_cnt; ///< count the number of codewords
        int m_frame_len; ///<length of the frame in number of items
        bool m_ldro; ///< use the low datarate optimisation mode
        int m_bw;
        uint8_t m_ldro_mode; ///< mode of the low datarate optimisation (0: off, 1: on, 2: auto)
        tag_t m_config_tag;
        tag_t m_framelen_tag;
        bool m_has_config_tag; ///<indicate that a configuration tag was received


     public:
      interleaver_impl(uint8_t cr, uint8_t sf, uint8_t ldro_mode, int bw);
      ~interleaver_impl();

      void set_cr(uint8_t cr);
      uint8_t get_cr();
      void set_sf(uint8_t sf);
      void update_var(int new_cr, int new_sf, int new_bw);
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_INTERLEAVER_IMPL_H */
