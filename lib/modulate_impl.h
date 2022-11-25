#ifndef INCLUDED_LORA_MODULATE_IMPL_H
#define INCLUDED_LORA_MODULATE_IMPL_H

#include <gnuradio/lora_sdr/modulate.h>
#include <gnuradio/io_signature.h>
#include <iostream>
#include <fstream>

#include <gnuradio/lora_sdr/utilities.h>

// #define GR_LORA_PRINT_INFO

namespace gr {
  namespace lora_sdr {

    class modulate_impl : public modulate
    {
     private:
        uint8_t m_sf; ///< Transmission spreading factor
        uint32_t m_samp_rate; ///< Transmission sampling rate
        uint32_t m_bw; ///< Transmission bandwidth (Works only for samp_rate=bw)
        uint32_t m_number_of_bins; ///< number of bin per loar symbol
        uint32_t m_samples_per_symbol; ///< samples per symbols(Works only for 2^sf)
        std::vector<uint16_t> m_sync_words; ///< sync words (network id) 

        int m_ninput_items_required; ///< number of samples required to call this block (forecast)

        int m_os_factor; ///< ovesampling factor based on sampling rate and bandwidth

        uint32_t m_inter_frame_padding; ///< length in samples of zero append to each frame

        int m_frame_len;///< leng of the frame in number of items

        std::vector<gr_complex> m_upchirp; ///< reference upchirp
        std::vector<gr_complex> m_downchirp; ///< reference downchirp

        uint16_t m_preamb_len; ///< number of upchirps in the preamble
        int32_t samp_cnt; ///< counter of the number of lora samples sent
        uint32_t preamb_samp_cnt; ///< counter of the number of preamble symbols output
        uint32_t padd_cnt; ///< counter of the number of null symbols output after each frame
        uint64_t frame_cnt; ///< counter of the number of frame sent
        bool frame_end; ///< indicate that we send a full frame


     public:
      modulate_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw, std::vector<uint16_t> sync_words, uint32_t frame_zero_padd, uint16_t preamb_len);
      ~modulate_impl();

      void set_sf(uint8_t sf);

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_MODULATE_IMPL_H */
