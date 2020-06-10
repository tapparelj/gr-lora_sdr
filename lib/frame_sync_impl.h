
#ifndef INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H
// #define GRLORA_DEBUG
// #define GRLORA_MEASUREMENTS

#include <lora_sdr/frame_sync.h>
#include <iostream>
#include <fstream>
#include <volk/volk.h>
#include <lora_sdr/utilities.h>
#include <gnuradio/io_signature.h>
extern "C" {
  #include "kiss_fft.h"
}

namespace gr {
  namespace lora_sdr {

    class frame_sync_impl : public frame_sync
    {
     private:
         enum DecoderState {
             DETECT,
             SYNC,
             FRAC_CFO_CORREC,
             STOP
         };
         enum SyncState {
             NET_ID1,
             NET_ID2,
             DOWNCHIRP1,
             DOWNCHIRP2,
             QUARTER_DOWN
         };
         uint8_t m_state;        ///< Current state of the synchronization
         uint32_t m_bw;          ///< Bandwidth
         uint32_t m_samp_rate;   ///< Sampling rate
         uint8_t m_sf;           ///< Spreading factor
         uint8_t m_cr;           ///< Coding rate
         uint32_t m_pay_len;     ///< payload length
         uint8_t m_has_crc;      ///< CRC presence
         bool m_impl_head;       ///< use implicit header mode

         bool received_cr;               ///< Indicate that the coding rate has been given by the header_decoder block
         bool received_crc;              ///< Indicate that the crc presence has been given by the header_decoder block
         bool received_pay_len;          ///< Indicate that the payload length has been given by the header_decoder block


         uint32_t m_number_of_bins;      ///< Number of bins in each lora Symbol
         uint32_t m_samples_per_symbol;  ///< Number of samples received per lora symbols
         uint32_t symb_numb;             ///<number of payload loar symbols

         std::vector<gr_complex> in_down; ///< downsampled input
         std::vector<gr_complex> m_downchirp; ///< Reference downchirp
         std::vector<gr_complex> m_upchirp;   ///< Reference upchirp

         int32_t symbol_cnt;         ///< Number of symbols already received
         int32_t bin_idx;            ///< value of previous lora symbol
         int32_t bin_idx_new;        ///< value of newly demodulated symbol

         uint32_t n_up;              ///< Number of consecutive upchirps in preamble
         uint8_t symbols_to_skip;    ///< Number of integer symbol to skip after consecutive upchirps
         uint32_t net_id_1;          ///< network identifier 1
         uint32_t net_id_2;          ///<network identifier 2

         kiss_fft_cpx *cx_in;        ///<input of the FFT
         kiss_fft_cpx *cx_out;       ///<output of the FFT

         int items_to_consume;       ///< Number of items to consume after each iteration of the general_work function

         std::vector<gr_complex> preamble_raw;///<vector containing the preamble upchirps without any synchronization
         std::vector<gr_complex> preamble_up; ///<vector containing the preamble upchirps

         int up_symb_to_use; ///<number of upchirp symbols to use for CFO and STO frac estimation
         int k_hat;          ///<integer part of CFO+STO
         double lambda_cfo;  ///<fractional part of CFO
         double lambda_bernier; ///<fractional part of CFO using Berniers algo
         double lambda_sto;  ///<fractional part of CFO
         bool cfo_sto_est; ///< indicate that the estimation of lambda_cfo/sto has been performed
         int usFactor;       ///<upsampling factor used by the FIR interpolator
         std::vector<gr_complex> CFO_frac_correc; ///<cfo frac correction vector


         std::vector<gr_complex> symb_corr; ///< symbol with CFO frac corrected
         int down_val; ///< value of the preamble downchirps
         int CFOint; ///< integer part of CFO
         int net_id_off; ///<offset of the network identifier

         #ifdef GRLORA_MEASUREMENTS
         int off_by_one_id; ///< Indicate that the network identifiers where off by one and corrected
         std::ofstream sync_log; ///< savefile containing the offset estimation and the signal strength estimation
         #endif
         #ifdef GRLORA_DEBUG
         int numb_symbol_to_save;///< number of symbol to save for every erroneous frame
         std::vector<gr_complex> last_frame;///< vector storing samples of the last received frame
         std::ofstream samples_file;///< savefile containing the samples of the erroneous frames
         #endif

         void header_cr_handler(pmt::pmt_t cr);
         void header_pay_len_handler(pmt::pmt_t pay_len);
         void header_crc_handler(pmt::pmt_t crc);
         void frame_err_handler(pmt::pmt_t err);


         /**
          *  \brief  Estimate the value of fractional part of the CFO using RCTSL
          *  \param  samples
          *          The pointer to the preamble beginning.(We might want to avoid the
          *          first symbol since it might be incomplete)
          */
         void estimate_CFO(gr_complex* samples);
         /**
          *  \brief  (not used) Estimate the value of fractional part of the CFO using Berniers algorithm
          */
         void estimate_CFO_Bernier();
         /**
          *  \brief  Estimate the value of fractional part of the STO from m_consec_up
          **/
         void estimate_STO();
         /**
          *  \brief  Recover the lora symbol value using argmax of the dechirped symbol FFT.
          *
          *  \param  samples
          *          The pointer to the symbol beginning.
          *  \param  ref_chirp
          *          The reference chirp to use to dechirp the lora symbol.
          */
         uint32_t get_symbol_val(const gr_complex *samples,gr_complex *ref_chirp);

          /**
          *  \brief  Determine the energy of a symbol.
          *
          *  \param  samples
          *          The complex symbol to analyse.
          */
         float determine_energy(const gr_complex *samples);

          /**
          *  \brief  Handles the error message coming from the header decoding.
          */
         void header_err_handler(pmt::pmt_t payload_len);

     public:
      frame_sync_impl(float samp_rate, uint32_t bandwidth, uint8_t sf, bool impl_head);
      ~frame_sync_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_SYNC_IMPL_H */
