
#ifndef INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H
#define INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H
// #define GRLORA_DEBUG
// #define GRLORA_MEASUREMENTS

#include <lora_sdr/fft_demod.h>
#include <iostream>
#include <fstream>
#include <volk/volk.h>
#include <gnuradio/io_signature.h>
#include <lora_sdr/utilities.h>
#include <lora_sdr/fft_demod.h>
#include<lora_sdr/utilities.h>
namespace gr {
  namespace lora_sdr {

    class fft_demod_impl : public fft_demod
    {
    private:
      uint32_t m_bw;          ///< Bandwidth
      uint32_t m_samp_rate;   ///< Sampling rate
      uint8_t m_sf;           ///< Spreading factor
      uint8_t m_cr;           ///< Coding rate

      uint32_t m_number_of_bins;      ///< Number of bins in each lora Symbol
      uint32_t m_samples_per_symbol;  ///< Number of samples received per lora symbols
      int CFOint; ///< integer part of the CFO

      // variable used to perform the FFT demodulation
      std::vector<gr_complex> m_upchirp;   ///< Reference upchirp
      std::vector<gr_complex> m_downchirp; ///< Reference downchirp
      std::vector<gr_complex> m_dechirped; ///< Dechirped symbol
      std::vector<gr_complex> m_fft;       ///< Result of the FFT


      std::vector<uint32_t> output;   ///< Stores the value to be outputted once a full bloc has been received
      bool is_first;                  ///< Indicate that the first block hasn't been fully received
      uint8_t block_size;             ///< The number of lora symbol in one block
      bool received_cr;               ///< Indicate that the coding rate has been given by the header_decoder block
      bool received_crc;              ///< Indicate that the crc presence has been given by the header_decoder block
      bool received_pay_len;          ///< Indicate that the payload length has been given by the header_decoder block
      #ifdef GRLORA_MEASUREMENTS
      std::ofstream energy_file;
      #endif
      #ifdef GRLORA_DEBUG
      std::ofstream idx_file;
      #endif

      /**
       *  \brief  Recover the lora symbol value using argmax of the dechirped symbol FFT.
       *
       *  \param  samples
       *          The pointer to the symbol beginning.
       */
      int32_t get_symbol_val(const gr_complex *samples);

      /**
       *  \brief  Reset the block variables when a new lora packet needs to be decoded.
       */
      void new_frame_handler(pmt::pmt_t id);

      /**
       *  \brief  Handles the reception of the coding rate received by the header_decoder block.
       */
      void header_cr_handler(pmt::pmt_t cr);

     public:
      fft_demod_impl(float samp_rate, uint32_t bandwidth, uint8_t sf, bool impl_head);
      ~fft_demod_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H */
