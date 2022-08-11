
#ifndef INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H
#define INCLUDED_LORA_SDR_FFT_DEMOD_IMPL_H
// #define GRLORA_DEBUG
// #define GRLORA_MEASUREMENTS
//#define GRLORA_SNR_MEASUREMENTS_SAVE
//#define GRLORA_BESSEL_MEASUREMENTS_SAVE
//#define GRLORA_LLR_MEASUREMENTS_SAVE

#include <gnuradio/lora_sdr/fft_demod.h>
#include <iostream>
#include <fstream>
#include <volk/volk.h>
#include <gnuradio/io_signature.h>
#include <gnuradio/lora_sdr/utilities.h>
#include <gnuradio/lora_sdr/fft_demod.h>

namespace gr {
  namespace lora_sdr {

    class fft_demod_impl : public fft_demod
    {
    private:
      uint8_t m_sf;           ///< Spreading factor
      uint8_t m_cr;           ///< Coding rate
      bool m_soft_decoding;   ///< Hard/Soft decoding
      bool max_log_approx;     ///< use Max-log approximation in LLR formula
      bool m_new_frame;       ///< To be notify when receive a new frame to estimate SNR
      bool m_ldro; ///< use low datarate optimisation
      uint m_symb_numb; ///< number of symbols in the frame
      uint m_symb_cnt; ///< number of symbol already output in current frame

      double m_Ps_est = 0;   // Signal Power estimation updated at each rx symbol
      double m_Pn_est = 0;   // Signal Power estimation updated at each rx symbo

      uint32_t m_samples_per_symbol;  ///< Number of samples received per lora symbols
      int CFOint; ///< integer part of the CFO

      // variable used to perform the FFT demodulation
      std::vector<gr_complex> m_upchirp;   ///< Reference upchirp
      std::vector<gr_complex> m_downchirp; ///< Reference downchirp
      std::vector<gr_complex> m_dechirped; ///< Dechirped symbol
      std::vector<gr_complex> m_fft;       ///< Result of the FFT

      std::vector<uint16_t> output;   ///< Stores the value to be outputted once a full bloc has been received
      std::vector< std::vector<LLR> > LLRs_block; ///< Stores the LLRs to be outputted once a full bloc has been received
      bool is_header;                  ///< Indicate that the first block hasn't been fully received
      uint8_t block_size;             ///< The number of lora symbol in one block
     
      #ifdef GRLORA_MEASUREMENTS
      std::ofstream energy_file;
      #endif
      #ifdef GRLORA_DEBUG
      std::ofstream idx_file;
      #endif
      #ifdef GRLORA_SNR_MEASUREMENTS_SAVE
      std::ofstream SNRestim_file;
      #endif
      #ifdef GRLORA_BESSEL_MEASUREMENTS_SAVE
      std::ofstream bessel_file;
      #endif

      /**
       *  \brief  Recover the lora symbol value using argmax of the dechirped symbol FFT.
       *
       *  \param  samples
       *          The pointer to the symbol beginning.
       */
      uint16_t get_symbol_val(const gr_complex *samples);

      /**
       * @brief Set spreading factor and init vector sizes accordingly
       * 
       */
      void set_sf(int sf);

      /**
       *  \brief  Reset the block variables when a new lora packet needs to be decoded.
       */
      void new_frame_handler(int cfo_int);

      /**
       *  \brief  Handles the reception of the coding rate received by the header_decoder block.
       */
      void header_cr_handler(pmt::pmt_t cr);

      /**
       *  \brief  Compute the FFT and fill the class attributes
       */
      float* compute_fft_mag(const gr_complex *samples);

      /**
       *  \brief  Compute the Log-Likelihood Ratios of the SF nbr of bits
       */
      std::vector<LLR> get_LLRs(const gr_complex *samples);

     public:
      fft_demod_impl( bool soft_decoding, bool max_log_approx);
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
