#include "frame_sync_impl.h"
#include <gnuradio/io_signature.h>
// Fix for libboost > 1.75
#include <boost/bind/placeholders.hpp>

using namespace boost::placeholders;
namespace gr {
namespace lora_sdr {

frame_sync::sptr frame_sync::make(float samp_rate, uint32_t bandwidth,
                                  uint8_t sf, bool impl_head) {
  return gnuradio::get_initial_sptr(
      new frame_sync_impl(samp_rate, bandwidth, sf, impl_head));
}

/**
 * @brief Construct a new frame sync impl object
 *
 * @param samp_rate : sampling rate
 * @param bandwidth : bandwidth
 * @param sf : spreading factor
 * @param impl_head : boolean to tell if implicit header mode is used
 */
frame_sync_impl::frame_sync_impl(float samp_rate, uint32_t bandwidth,
                                 uint8_t sf, bool impl_head)
    : gr::block("frame_sync", gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(0, 1, (1u << sf) * sizeof(gr_complex))) {
  m_state = DETECT;
  m_bw = bandwidth;
  m_samp_rate = samp_rate;
  m_sf = sf;
  symbols_to_skip = 4;
  n_up = 8;
  net_id_1 = 8; // should be different from 2^sf-1, 0 and 1
  net_id_2 = 16;
  up_symb_to_use = 6;

  usFactor = 4;
  lambda_sto = 0;

  m_impl_head = impl_head;

  m_number_of_bins = (uint32_t)(1u << m_sf);
  m_samples_per_symbol = (uint32_t)(m_samp_rate * m_number_of_bins / m_bw);

  m_upchirp.resize(m_samples_per_symbol);
  m_downchirp.resize(m_samples_per_symbol);
  preamble_up.resize(n_up * m_samples_per_symbol);
  CFO_frac_correc.resize(m_samples_per_symbol);
  symb_corr.resize(m_samples_per_symbol);
  in_down.resize(m_number_of_bins);
  preamble_raw.resize(n_up * m_samples_per_symbol);

  build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

  bin_idx = 0;
  symbol_cnt = 1;
  k_hat = 0;

  cx_in = new kiss_fft_cpx[m_samples_per_symbol];
  cx_out = new kiss_fft_cpx[m_samples_per_symbol];
  // register message ports
  message_port_register_out(pmt::mp("new_frame"));

  message_port_register_in(pmt::mp("CR"));
  set_msg_handler(pmt::mp("CR"),
                  boost::bind(&frame_sync_impl::header_cr_handler, this, _1));

  message_port_register_in(pmt::mp("pay_len"));
  set_msg_handler(
      pmt::mp("pay_len"),
      boost::bind(&frame_sync_impl::header_pay_len_handler, this, _1));

  message_port_register_in(pmt::mp("crc"));
  set_msg_handler(pmt::mp("crc"),
                  boost::bind(&frame_sync_impl::header_crc_handler, this, _1));

  message_port_register_in(pmt::mp("err"));
  set_msg_handler(pmt::mp("err"),
                  boost::bind(&frame_sync_impl::header_err_handler, this, _1));

  message_port_register_in(pmt::mp("frame_err"));
  set_msg_handler(pmt::mp("frame_err"),
                  boost::bind(&frame_sync_impl::frame_err_handler, this, _1));
  // #ifdef GRLORA_DEBUG
  //     // numb_symbol_to_save=80;//number of symbol per erroneous frame to
  //     save
  //     // last_frame.resize(m_samples_per_symbol*numb_symbol_to_save);
  //     // samples_file.open("../matlab/err_symb.txt", std::ios::out |
  //     std::ios::trunc );
  // #endif
  set_tag_propagation_policy(TPP_ALL_TO_ALL);
}

/**
 * @brief Destroy the frame sync impl object
 *
 */
frame_sync_impl::~frame_sync_impl() {}

/**
 * @brief Standard gnuradio function to tell the system
 * how many input items are needed to produce one output item
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of required input items
 */
void frame_sync_impl::forecast(int noutput_items,
                               gr_vector_int &ninput_items_required) {
  // TODO fix : for sf=11 and sf=12
  ninput_items_required[0] = usFactor * (m_samples_per_symbol + 2);
  // if(m_sf <= 10){
  //   ninput_items_required[0] = usFactor * (m_samples_per_symbol + 2);
  // }
  // if()
}

/**
 * @brief Estimate the value of fractional part of the CFO using RCTSL
 *
 * @param samples The pointer to the preamble beginning.(We might want to
 * avoid the first symbol since it might be incomplete)
 */
void frame_sync_impl::estimate_CFO(gr_complex *samples) {
  // DFt frequency bin index
  int k0;
  //
  double Y_min, Y0, Y_plus, u, v, ka, wa, k_residual;
  //< CFO frac correction vector
  std::vector<gr_complex> CFO_frac_correc_aug(up_symb_to_use *
                                              m_number_of_bins);
  // dechirped signal
  std::vector<gr_complex> dechirped(up_symb_to_use * m_number_of_bins);
  // DFT variables
  kiss_fft_cpx *cx_in_cfo =
      new kiss_fft_cpx[2 * up_symb_to_use * m_samples_per_symbol];
  kiss_fft_cpx *cx_out_cfo =
      new kiss_fft_cpx[2 * up_symb_to_use * m_samples_per_symbol];
  // sqaure of DFT signal
  float fft_mag_sq[2 * up_symb_to_use * m_number_of_bins];
  kiss_fft_cfg cfg_cfo =
      kiss_fft_alloc(2 * up_symb_to_use * m_samples_per_symbol, 0, 0, 0);

  // create longer downchirp
  std::vector<gr_complex> downchirp_aug(up_symb_to_use * m_number_of_bins);
  for (int i = 0; i < up_symb_to_use; i++) {
    memcpy(&downchirp_aug[i * m_number_of_bins], &m_downchirp[0],
           m_number_of_bins * sizeof(gr_complex));
  }

  // Dechirping
  volk_32fc_x2_multiply_32fc(&dechirped[0], samples, &downchirp_aug[0],
                             up_symb_to_use * m_samples_per_symbol);
  // prepare FFT
  for (int i = 0; i < 2 * up_symb_to_use * m_samples_per_symbol; i++) {
    if (i < up_symb_to_use * m_samples_per_symbol) {
      cx_in_cfo[i].r = dechirped[i].real();
      cx_in_cfo[i].i = dechirped[i].imag();
    } else {
      // zero add padding to the DFT signal
      cx_in_cfo[i].r = 0;
      cx_in_cfo[i].i = 0;
    }
  }
  // do the FFT
  kiss_fft(cfg_cfo, cx_in_cfo, cx_out_cfo);
  // make the sqaure DFT signal

  // TODO:check optimization possible first find Y_plus, Y_min, Y and then
  // square those only
  for (uint32_t i = 0u; i < 2 * up_symb_to_use * m_samples_per_symbol; i++) {
    fft_mag_sq[i] =
        cx_out_cfo[i].r * cx_out_cfo[i].r + cx_out_cfo[i].i * cx_out_cfo[i].i;
  }
  free(cfg_cfo);
  // get index of maximal frequency bin of DFT
  k0 = ((std::max_element(fft_mag_sq,
                          fft_mag_sq + 2 * up_symb_to_use * m_number_of_bins) -
         fft_mag_sq));

  // Y-1
  Y_min = fft_mag_sq[mod(k0 - 1, 2 * up_symb_to_use * m_number_of_bins)];
  // Y normal
  Y0 = fft_mag_sq[k0];
  // Y+1
  Y_plus = fft_mag_sq[mod(k0 + 1, 2 * up_symb_to_use * m_number_of_bins)];
  // set constant coeff from Cui yang (15)
  u = 64 * m_number_of_bins / 406.5506497;
  v = u * 2.4674;
  // preform RCTSL
  wa = (Y_plus - Y_min) / (u * (Y_plus + Y_min) + v * Y0);
  // get k_alpha
  ka = wa * m_number_of_bins / M_PI;
  //
  k_residual = fmod((k0 + ka) / 2 / up_symb_to_use, 1);
  // compute actual fractal offset
  lambda_cfo = k_residual - (k_residual > 0.5 ? 1 : 0);
  // Correct CFO in preamble
  for (int n = 0; n < up_symb_to_use * m_number_of_bins; n++) {
    CFO_frac_correc_aug[n] =
        gr_expj(-2 * M_PI * lambda_cfo / m_number_of_bins * n);
  }
  volk_32fc_x2_multiply_32fc(&preamble_up[0], samples, &CFO_frac_correc_aug[0],
                             up_symb_to_use * m_number_of_bins);
}

/**
 * @brief (not used) Estimate the value of fractional part of the CFO using
 * Berniers algorithm
 *
 */
void frame_sync_impl::estimate_CFO_Bernier() {
  int k0[m_number_of_bins];
  double k0_mag[m_number_of_bins];
  std::vector<gr_complex> fft_val(up_symb_to_use * m_number_of_bins);

  std::vector<gr_complex> dechirped(m_number_of_bins);
  kiss_fft_cpx *cx_in_cfo = new kiss_fft_cpx[m_samples_per_symbol];
  kiss_fft_cpx *cx_out_cfo = new kiss_fft_cpx[m_samples_per_symbol];
  float fft_mag_sq[m_number_of_bins];
  for (size_t i = 0; i < m_number_of_bins; i++) {
    fft_mag_sq[i] = 0;
  }
  kiss_fft_cfg cfg_cfo = kiss_fft_alloc(m_samples_per_symbol, 0, 0, 0);

  for (int i = 0; i < up_symb_to_use; i++) {
    // Dechirping
    volk_32fc_x2_multiply_32fc(
        &dechirped[0],
        &preamble_raw[(m_number_of_bins - k_hat) + m_number_of_bins * i],
        &m_downchirp[0], m_samples_per_symbol);
    // prepare FFT
    for (int i = 0; i < m_samples_per_symbol; i++) {
      cx_in_cfo[i].r = dechirped[i].real();
      cx_in_cfo[i].i = dechirped[i].imag();
    }
    // do the FFT
    kiss_fft(cfg_cfo, cx_in_cfo, cx_out_cfo);
    // Get magnitude

    for (uint32_t j = 0u; j < m_samples_per_symbol; j++) {
      fft_mag_sq[j] =
          cx_out_cfo[j].r * cx_out_cfo[j].r + cx_out_cfo[j].i * cx_out_cfo[j].i;
      fft_val[j + i * m_samples_per_symbol] =
          gr_complex(cx_out_cfo[j].r, cx_out_cfo[j].i);
    }
    k0[i] = std::max_element(fft_mag_sq, fft_mag_sq + m_number_of_bins) -
            fft_mag_sq;

    k0_mag[i] = fft_mag_sq[k0[i]];
  }
  free(cfg_cfo);
  // get argmax
  int idx_max =
      k0[std::max_element(k0_mag, k0_mag + m_number_of_bins) - k0_mag];

  gr_complex four_cum(0.0f, 0.0f);
  for (int i = 0; i < up_symb_to_use - 1; i++) {
    four_cum += fft_val[idx_max + m_number_of_bins * i] *
                std::conj(fft_val[idx_max + m_number_of_bins * (i + 1)]);
  }
  lambda_bernier = -std::arg(four_cum) / 2 / M_PI;
}

/**
 * @brief Estimate the value of fractional part of the STO from m_consec_up
 *
 */
void frame_sync_impl::estimate_STO() {
  // DFT bin index
  int k0;
  //
  double Y_min, Y0, Y_plus, u, v, ka, wa, k_residual;
  // dechirped vector
  std::vector<gr_complex> dechirped(m_number_of_bins);
  // DFT variables
  kiss_fft_cpx *cx_in_cfo = new kiss_fft_cpx[2 * m_samples_per_symbol];
  kiss_fft_cpx *cx_out_cfo = new kiss_fft_cpx[2 * m_samples_per_symbol];
  // variable to hold the sqaure of the fft
  float fft_mag_sq[2 * m_number_of_bins];
  // compute square of fft
  for (size_t i = 0; i < 2 * m_number_of_bins; i++) {
    fft_mag_sq[i] = 0;
  }
  // fft memory allocation
  kiss_fft_cfg cfg_cfo = kiss_fft_alloc(2 * m_samples_per_symbol, 0, 0, 0);

  for (int i = 0; i < up_symb_to_use; i++) {
    // Dechirping
    volk_32fc_x2_multiply_32fc(&dechirped[0],
                               &preamble_up[m_number_of_bins * i],
                               &m_downchirp[0], m_samples_per_symbol);
    // prepare FFT
    for (int i = 0; i < 2 * m_samples_per_symbol; i++) {
      if (i < m_samples_per_symbol) {
        cx_in_cfo[i].r = dechirped[i].real();
        cx_in_cfo[i].i = dechirped[i].imag();
      } else {
        // zero add padding to DFT
        cx_in_cfo[i].r = 0;
        cx_in_cfo[i].i = 0;
      }
    }
    // do the FFT
    kiss_fft(cfg_cfo, cx_in_cfo, cx_out_cfo);
    // Get magnitude
    for (uint32_t i = 0u; i < 2 * m_samples_per_symbol; i++) {
      fft_mag_sq[i] +=
          cx_out_cfo[i].r * cx_out_cfo[i].r + cx_out_cfo[i].i * cx_out_cfo[i].i;
    }
  }
  free(cfg_cfo);

  // get DFT bin index
  k0 = std::max_element(fft_mag_sq, fft_mag_sq + 2 * m_number_of_bins) -
       fft_mag_sq;

  // get DFT at k0 - 1
  Y_min = fft_mag_sq[mod(k0 - 1, 2 * m_number_of_bins)];
  // get DFT at k0
  Y0 = fft_mag_sq[k0];
  // get DFT at k0 + 1
  Y_plus = fft_mag_sq[mod(k0 + 1, 2 * m_number_of_bins)];
  // set constant coeff from Cui yang (eq.15) to be used in RCTSL
  u = 64 * m_number_of_bins / 406.5506497;
  v = u * 2.4674;
  // RCTSL
  wa = (Y_plus - Y_min) / (u * (Y_plus + Y_min) + v * Y0);
  ka = wa * m_number_of_bins / M_PI;
  k_residual = fmod((k0 + ka) / 2, 1);
  // compute actual fractal offset of sto
  lambda_sto = k_residual - (k_residual > 0.5 ? 1 : 0);
}

/**
 * @brief Function that gets the symbol from the received samples
 *
 * @param samples : the complex samples
 * @param ref_chirp The reference chirp to use to dechirp the lora symbol.
 * @return uint32_t
 */
uint32_t frame_sync_impl::get_symbol_val(const gr_complex *samples,
                                         gr_complex *ref_chirp) {
  double sig_en = 0;
  float fft_mag[m_number_of_bins];
  std::vector<gr_complex> dechirped(m_number_of_bins);

  kiss_fft_cfg cfg = kiss_fft_alloc(m_samples_per_symbol, 0, 0, 0);

  // Multiply with ideal downchirp
  volk_32fc_x2_multiply_32fc(&dechirped[0], samples, ref_chirp,
                             m_samples_per_symbol);

  for (int i = 0; i < m_samples_per_symbol; i++) {
    cx_in[i].r = dechirped[i].real();
    cx_in[i].i = dechirped[i].imag();
  }
  // do the FFT
  kiss_fft(cfg, cx_in, cx_out);

  // Get magnitude
  for (uint32_t i = 0u; i < m_number_of_bins; i++) {
    fft_mag[i] = cx_out[i].r * cx_out[i].r + cx_out[i].i * cx_out[i].i;
    sig_en += fft_mag[i];
  }
  free(cfg);
  // Return argmax here
  return ((std::max_element(fft_mag, fft_mag + m_number_of_bins) - fft_mag));
}

/**
 * @brief Determine the energy of a symbol.
 *
 * @param samples the complex symbol to analyse.
 * @return float
 */
float frame_sync_impl::determine_energy(const gr_complex *samples) {
  float magsq_chirp[m_samples_per_symbol];
  float energy_chirp = 0;
  volk_32fc_magnitude_squared_32f(magsq_chirp, samples, m_samples_per_symbol);
  volk_32f_accumulator_s32f(&energy_chirp, magsq_chirp, m_samples_per_symbol);
  return energy_chirp;
}

/**
 * @brief Function that handles the coding rate from the header decoding stage
 *
 * @param cr : coding rate
 */
void frame_sync_impl::header_cr_handler(pmt::pmt_t cr) {
  // get coding rate from header decoder
  m_cr = pmt::to_long(cr);
  // set variable that we have an coding rate to true
  received_cr = true;
  if (received_cr && received_crc &&
      received_pay_len) // get number of symbol of the frame
    symb_numb = 8 + ceil((double)(2 * m_pay_len - m_sf + 2 + !m_impl_head * 5 +
                                  m_has_crc * 4) /
                         m_sf) *
                        (4 + m_cr);
};

/**
 * @brief Function that handles the payload length (i.e. data length) from the
 * header decoder stage
 *
 * @param pay_len :payload length
 */
void frame_sync_impl::header_pay_len_handler(pmt::pmt_t pay_len) {
  m_pay_len = pmt::to_long(pay_len);
  received_pay_len = true;
  if (received_cr && received_crc &&
      received_pay_len) // get number of symbol of the frame
    symb_numb = 8 + ceil((double)(2 * m_pay_len - m_sf + 2 + !m_impl_head * 5 +
                                  m_has_crc * 4) /
                         m_sf) *
                        (4 + m_cr);
};

/**
 * @brief Function to handle the crc of the header from the header decoder stage
 *
 * @param crc : crc
 */
void frame_sync_impl::header_crc_handler(pmt::pmt_t crc) {
  m_has_crc = pmt::to_long(crc);
  received_crc = true;
  if (received_cr && received_crc &&
      received_pay_len) // get number of symbol of the frame
    symb_numb = 8 + ceil((double)(2 * m_pay_len - m_sf + 2 + !m_impl_head * 5 +
                                  m_has_crc * 4) /
                         m_sf) *
                        (4 + m_cr);
};

/**
 * @brief Handles the error message coming from the header decoding.
 *
 * @param err : error message
 */
void frame_sync_impl::header_err_handler(pmt::pmt_t err) {
  GR_LOG_INFO(this->d_logger,
              "Error in header decoding, reverting to detecting the header" +
                  pmt::symbol_to_string(err));
  // Set sync state to detect and start over the synchronisation
  m_state = DETECT;
  symbol_cnt = 1;
};

/**
 * @brief Handles frame errors coming from the header decoding stage
 *
 * @param err : error message
 */
void frame_sync_impl::frame_err_handler(pmt::pmt_t err) {
  GR_LOG_INFO(this->d_logger,
              "Error in frame decoding:" + pmt::symbol_to_string(err));
  // #ifdef GRLORA_DEBUG
  //   // for(int j=0;j<numb_symbol_to_save;j++){
  //   //     for(int i=0;i<m_number_of_bins;i++)
  //   //
  //   samples_file<<last_frame[i+m_number_of_bins*j].real()<<(last_frame[i+m_number_of_bins*j].imag()<0?"-":"+")<<std::abs(last_frame[i+m_number_of_bins*j].imag())
  //   //         <<"i,";
  //   // samples_file<<std::endl;
  //   // }
  //   std::cout << "saved one frame" << '\n';
  // #endif
};

/**
 * @brief Main function where the main logic and computation resides.
 * Function will find the window of samples and preform several estimates
 * to synchronies the internal window of samples to have been received (i.e.
 * align them in time and frequency)
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items, may be larger then 1
 * @param input_items : input items
 * @param output_items : output items (i.e. start of Rx decoding)
 * @return int
 */
int frame_sync_impl::general_work(int noutput_items,
                                  gr_vector_int &ninput_items,
                                  gr_vector_const_void_star &input_items,
                                  gr_vector_void_star &output_items) {
  // cast input and output to the right format (i.e. gr_complex)
  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];

  std::vector<tag_t> return_tag;
  get_tags_in_range(return_tag, 0, 0, nitems_read(0) + 1000000000);
  if (return_tag.size() > 0) {
    std::cout << "Frame Sync Done" << std::endl;
    add_item_tag(0, nitems_written(0), pmt::intern("status"),
                 pmt::intern("done"));
    consume_each(ninput_items[0]);
    return 10;
  } else {

    // downsampling
    for (int ii = 0; ii < m_number_of_bins; ii++) {
      in_down[ii] = in[(int)(usFactor - 1 + usFactor * ii -
                             round(lambda_sto * usFactor))];
    }

    // switch case to distinguish between the possible sync states
    switch (m_state) {
    // detect preamble
    case DETECT: {
      /**
       * @brief Detect preamble.
       * In order to detect preamble we start looking for consecutive symbols
       * (with a margin of ±1) (The +- 1 margin is needed for the possible
       * fractal part offset)
       *
       */
      // get value of symbol
      bin_idx_new = get_symbol_val(&in_down[0], &m_downchirp[0]);

      // First search for consecutive symbols with symbol {s+1,s,s-1}
      if (std::abs(bin_idx_new - bin_idx) <= 1) {
        // we should also add the first symbol value
        if (symbol_cnt == 1) {
          k_hat += bin_idx;
        }
        // set integer offset to the value of the demoudlated symbol
        k_hat += bin_idx_new;
        memcpy(&preamble_raw[m_samples_per_symbol * symbol_cnt], &in_down[0],
               m_samples_per_symbol * sizeof(gr_complex));
        symbol_cnt++;
      }
      // no consecutive symbols found
      else {
        memcpy(&preamble_raw[0], &in_down[0],
               m_samples_per_symbol * sizeof(gr_complex));
        symbol_cnt = 1;
        k_hat = 0;
      }
      // set index of symbol
      bin_idx = bin_idx_new;
      // if the number of consecutive symbols is n_up -1 (number of consecutive
      // symbols) -1 we have found the preamble
      if (symbol_cnt == (int)(n_up - 1)) {
        // preamble synchronisation is done !, set new sync state
        m_state = SYNC;
        // clear variables
        symbol_cnt = 0;
        cfo_sto_est = false;
        // set the integer offset
        k_hat = round(k_hat / (n_up - 1));
        // perform coarse synchronization, i.e shift the samples inside the
        // buffer
        items_to_consume = usFactor * (m_samples_per_symbol - k_hat);
      }
      // preamble sync not completed
      else {
        items_to_consume = usFactor * m_samples_per_symbol;
      }
      // set number of output items to be 0, since output is only used for
      // synchronisation and no output
      noutput_items = 0;
      break;
    }
    // synchronize integer part CFO and STO
    case SYNC: {
      /**
       * @brief Synchronize integer part STO,CFO
       * We have preamble detection, now we need part 2 of synchronisation
       * synchronisation of integer part of STO and CFO
       */
      // if there is no estimation of the fractal offset
      if (!cfo_sto_est) {
        // preform CFO estimate
        estimate_CFO(&preamble_raw[m_number_of_bins - k_hat]);
        // preform STO estimate
        estimate_STO();
        // create CFO correction vector
        for (int n = 0; n < m_number_of_bins; n++) {
          CFO_frac_correc[n] =
              gr_expj(-2 * M_PI * lambda_cfo / m_number_of_bins * n);
        }
        // set estimation of fractal part of offset to be true
        cfo_sto_est = true;
      }
      items_to_consume = usFactor * m_samples_per_symbol;
      // apply cfo correction
      volk_32fc_x2_multiply_32fc(&symb_corr[0], &in_down[0],
                                 &CFO_frac_correc[0], m_samples_per_symbol);

      bin_idx = get_symbol_val(&symb_corr[0], &m_downchirp[0]);
      //
      switch (symbol_cnt) {
        /**
         * @brief
         *
         */
      case NET_ID1: {
        /**
         * @brief Network identifier 1
         *
         */

        if (bin_idx == 0 || bin_idx == 1 || bin_idx == m_number_of_bins - 1) {
          // TODO: look for additional upchirps. Won't work if
          // network identifier 1 equals 2^sf-1, 0 or 1!
        }
        // wrong network identifier
        else if (labs(bin_idx - net_id_1) > 1) {
          // start again with detecting the preamble
          m_state = DETECT;
          symbol_cnt = 1;
          noutput_items = 0;
          k_hat = 0;
          lambda_sto = 0;
        }
        // network identifier 1 correct or off by one
        else {
          net_id_off = bin_idx - net_id_1;
          // try the second network identifier
          symbol_cnt = NET_ID2;
        }
        break;
      }
      case NET_ID2: {
        /**
         * @brief Network identifier 2
         *
         */
        // we got the wrong network identifier
        if (labs(bin_idx - net_id_2) > 1) {
          // start again with detecting the preamble
          m_state = DETECT;
          symbol_cnt = 1;
          noutput_items = 0;
          k_hat = 0;
          lambda_sto = 0;
        } else if (net_id_off && (bin_idx - net_id_2) == net_id_off) {
          // correct case off by one net id
          items_to_consume -= usFactor * net_id_off;
          symbol_cnt = DOWNCHIRP1;
        } else {
          symbol_cnt = DOWNCHIRP1;
        }
        break;
      }
      // TODO: find out why this is needed ?
      case DOWNCHIRP1:
        /**
         * @brief
         *
         */
        symbol_cnt = DOWNCHIRP2;
        break;
      case DOWNCHIRP2: {
        /**
         * @brief
         *
         */
        // get value of the preamble downchirp
        down_val = get_symbol_val(&symb_corr[0], &m_upchirp[0]);
        symbol_cnt = QUARTER_DOWN;
        break;
      }
      case QUARTER_DOWN: {
        /**
         * @brief the extra quater downschirp symbol present in the LoRa
         * preamble
         *
         */
        //
        if (down_val < m_number_of_bins / 2) {
          // get integer part of CFO
          CFOint = floor(down_val / 2);
// set point for new frame
#ifdef GRLORA_DEBUG
          GR_LOG_DEBUG(this->d_logger,
                       "DEBUG:CFOint:" + std::to_string(CFOint));
#endif

          message_port_pub(pmt::intern("new_frame"), pmt::mp((long)CFOint));
        }
        // TODO: figure outlogic behind
        else {
          //
          CFOint = ceil(double(down_val - (int)m_number_of_bins) / 2);
          // set point for new frame
          message_port_pub(
              pmt::intern("new_frame"),
              pmt::mp((long)((m_number_of_bins + CFOint) % m_number_of_bins)));
#ifdef GRLORA_DEBUG
          GR_LOG_DEBUG(this->d_logger,
                       "DEBUG:CFOint:" +
                           std::to_string(((m_number_of_bins + CFOint) %
                                           m_number_of_bins)));
#endif
        }
        items_to_consume =
            usFactor * m_samples_per_symbol / 4 + usFactor * CFOint;
        symbol_cnt = 0;
        // set new sync state to correct fractal part of CFO i.e. apply with
        // complex exponential
        m_state = FRAC_CFO_CORREC;
      }
        // end case count symb
      }
      noutput_items = 0;
      break;
      // end case SYNC
    }
    case FRAC_CFO_CORREC: {
      /**
       * @brief synchronize the fractal part of the CFO
       *
       */
      // transmitt only useful symbols (at least 8 symbol)
      if (symbol_cnt < symb_numb ||
          !(received_cr && received_crc && received_pay_len)) {
        // apply fractional cfo correction
        volk_32fc_x2_multiply_32fc(out, &in_down[0], &CFO_frac_correc[0],
                                   m_samples_per_symbol);
        //   #ifdef GRLORA_DEBUG
        // //   if(symbol_cnt<numb_symbol_to_save)
        // //
        // memcpy(&last_frame[symbol_cnt*m_number_of_bins],&in_down[0],m_samples_per_symbol*sizeof(gr_complex));
        //   #endif
        items_to_consume = usFactor * m_samples_per_symbol;
        noutput_items = 1;
        symbol_cnt++;
      }
      // Error revert to the preamble detecting case
      else {
        m_state = DETECT;
        // clear all variables
        symbol_cnt = 1;
        items_to_consume = usFactor * m_samples_per_symbol;
        noutput_items = 0;
        k_hat = 0;
        lambda_sto = 0;
      }
      break;
    }
    default: {
      GR_LOG_WARN(this->d_logger, "WARNING : No state! Shouldn't happen");
      break;
    }
    }
    consume_each(items_to_consume);
    return noutput_items;
  }
}
} /* namespace lora_sdr */
} /* namespace gr */
