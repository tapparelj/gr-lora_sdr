
#ifndef INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H
// #define GRLORA_DEBUG
// #define PRINT_INFO

#include <gnuradio/lora_sdr/frame_sync.h>
#include <iostream>
#include <fstream>
#include <volk/volk.h>
#include <gnuradio/lora_sdr/utilities.h>
#include <gnuradio/io_signature.h>
extern "C"
{
#include "kiss_fft.h"
}

namespace gr
{
  namespace lora_sdr
  {

    class frame_sync_impl : public frame_sync
    {
    private:
      enum DecoderState
      {
        DETECT,
        SYNC,
        SFO_COMPENSATION,
        STOP
      };
      enum SyncState
      {
        NET_ID1,
        NET_ID2,
        DOWNCHIRP1,
        DOWNCHIRP2,
        QUARTER_DOWN
      };
      uint8_t m_state;                    ///< Current state of the synchronization
      uint32_t m_center_freq;             ///< RF center frequency
      uint32_t m_bw;                      ///< Bandwidth
      uint32_t m_samp_rate;               ///< Sampling rate
      uint8_t m_sf;                       ///< Spreading factor
      uint8_t m_cr;                       ///< Coding rate
      uint32_t m_pay_len;                 ///< payload length
      uint8_t m_has_crc;                  ///< CRC presence
      uint8_t m_invalid_header;           ///< invalid header checksum
      bool m_impl_head;                   ///< use implicit header mode
      uint8_t m_os_factor;                ///< oversampling factor
      std::vector<uint16_t> m_sync_words; ///< vector containing the two sync words (network identifiers)
      bool m_ldro;                        ///< use of low datarate optimisation mode

      uint8_t m_n_up_req;            ///< number of consecutive upchirps required to trigger a detection

      uint32_t m_number_of_bins;     ///< Number of bins in each lora Symbol
      uint32_t m_samples_per_symbol; ///< Number of samples received per lora symbols
      uint32_t m_symb_numb;          ///<number of payload lora symbols
      bool m_received_head;          ///< indicate that the header has be decoded and received by this block
      double m_noise_est;            ///< estimate of the noise

      std::vector<gr_complex> in_down;     ///< downsampled input
      std::vector<gr_complex> m_downchirp; ///< Reference downchirp
      std::vector<gr_complex> m_upchirp;   ///< Reference upchirp

      uint frame_cnt;      ///< Number of frame received
      int32_t symbol_cnt;  ///< Number of symbols already received
      int32_t bin_idx;     ///< value of previous lora symbol
      int32_t bin_idx_new; ///< value of newly demodulated symbol

      uint16_t m_preamb_len; ///< Number of consecutive upchirps in preamble
      uint8_t additional_upchirps; ///< indicate the number of additional upchirps found in preamble (in addition to the minimum required to trigger a detection)

      kiss_fft_cpx *cx_in;  ///<input of the FFT
      kiss_fft_cpx *cx_out; ///<output of the FFT

      int items_to_consume; ///< Number of items to consume after each iteration of the general_work function

      int one_symbol_off; ///< indicate that we are offset by one symbol after the preamble 
      std::vector<gr_complex> additional_symbol_samp;  ///< save the value of the last 1.25 downchirp as it might contain the first payload symbol
      std::vector<gr_complex> preamble_raw;      ///<vector containing the preamble upchirps without any synchronization
      std::vector<gr_complex> preamble_raw_up;  ///<vector containing the upsampled preamble upchirps without any synchronization
      std::vector<gr_complex> downchirp_raw;    ///< vetor containing the preamble downchirps without any synchronization
      std::vector<gr_complex> preamble_upchirps; ///<vector containing the preamble upchirps
      std::vector<gr_complex> net_id_samp;       ///< vector of the oversampled network identifier samples
      std::vector<int> net_ids;                  ///< values of the network identifiers received

      int up_symb_to_use;              ///< number of upchirp symbols to use for CFO and STO frac estimation
      int k_hat;                       ///< integer part of CFO+STO
      std::vector<int> preamb_up_vals; ///< value of the preamble upchirps

      float m_cfo_frac;                            ///< fractional part of CFO
      float m_cfo_frac_bernier;                    ///< fractional part of CFO using Berniers algo
      int m_cfo_int;                               ///< integer part of CFO
      float m_sto_frac;                            ///< fractional part of CFO
      float sfo_hat;                               ///< estimated sampling frequency offset
      float sfo_cum;                               ///< cumulation of the sfo
      bool cfo_frac_sto_frac_est;                  ///< indicate that the estimation of CFO_frac and STO_frac has been performed
      std::vector<gr_complex> CFO_frac_correc;     ///< cfo frac correction vector
      std::vector<gr_complex> CFO_SFO_frac_correc; ///< correction vector accounting for cfo and sfo

      std::vector<gr_complex> symb_corr; ///< symbol with CFO frac corrected
      int down_val;                      ///< value of the preamble downchirps
      int net_id_off;                    ///< offset of the network identifier

      bool m_should_log;   ///< indicate that the sync values should be logged
      float off_by_one_id; ///< Indicate that the network identifiers where off by one and corrected (float used as saved in a float32 bin file)
#ifdef GRLORA_DEBUG
      std::ofstream preamb_file;
#endif
      // std::ofstream start_off_file;
      // std::ofstream netid_file;
      int my_roundf(float number);
      
      /**
          *  \brief  Estimate the value of fractional part of the CFO using RCTSL and correct the received preamble accordingly
          *  \param  samples
          *          The pointer to the preamble beginning.(We might want to avoid the
          *          first symbol since it might be incomplete)
          */
      float estimate_CFO_frac(gr_complex *samples);
      /**
          *  \brief  (not used) Estimate the value of fractional part of the CFO using Berniers algorithm and correct the received preamble accordingly
          *  \param  samples
          *          The pointer to the preamble beginning.(We might want to avoid the
          *          first symbol since it might be incomplete)
          */
      float estimate_CFO_frac_Bernier(gr_complex *samples);
      /**
          *  \brief  Estimate the value of fractional part of the STO from m_consec_up and returns the estimated value
          * 
          **/
      float estimate_STO_frac();
      /**
          *  \brief  Recover the lora symbol value using argmax of the dechirped symbol FFT. Returns -1 in case of an fft window containing no energy to handle noiseless simulations.
          *
          *  \param  samples
          *          The pointer to the symbol beginning.
          *  \param  ref_chirp
          *          The reference chirp to use to dechirp the lora symbol.
          */
      uint32_t get_symbol_val(const gr_complex *samples, gr_complex *ref_chirp);
      

      /**
          *  \brief  Determine the energy of a symbol.
          *
          *  \param  samples
          *          The complex symbol to analyse.
          *          length
          *          The number of LoRa symbols used for the estimation
          */
      float determine_energy(const gr_complex *samples, int length);

      /**
         *   \brief  Handle the reception of the explicit header information, received from the header_decoder block 
         */
      void frame_info_handler(pmt::pmt_t frame_info);

      /**
          *  \brief  Handles reception of the noise estimate
          */
      void noise_est_handler(pmt::pmt_t noise_est);
      /**
          *  \brief  Set new SF received in a tag (used for CRAN)
          */
      void set_sf(int sf);

      float determine_snr(const gr_complex *samples);

    public:
      frame_sync_impl(uint32_t center_freq, uint32_t bandwidth, uint8_t sf, bool impl_head, std::vector<uint16_t> sync_word, uint8_t os_factor, uint16_t preamb_len);
      ~frame_sync_impl();

      // Where all the action really happens
      void forecast(int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H */
