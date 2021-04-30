#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "frame_sync_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

frame_sync::sptr frame_sync::make(float samp_rate, uint32_t bandwidth,
                                  uint8_t sf, bool impl_head,
                                  std::vector<uint16_t> sync_word) {
  return gnuradio::get_initial_sptr(
      new frame_sync_impl(samp_rate, bandwidth, sf, impl_head, sync_word));
}

/**
 * @brief Construct a new frame sync impl::frame sync impl object
 *
 * @param samp_rate
 * @param bandwidth
 * @param sf
 * @param impl_head
 * @param sync_word
 */
frame_sync_impl::frame_sync_impl(float samp_rate, uint32_t bandwidth,
                                 uint8_t sf, bool impl_head,
                                 std::vector<uint16_t> sync_word)
    : gr::block("frame_sync", gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(0, 1, (1u << sf) * sizeof(gr_complex))) {
  gr::thread::thread_bind_to_processor(1);
  gr::block::set_thread_priority(92);
  m_state = DETECT;
  m_bw = bandwidth;
  m_samp_rate = samp_rate;
  m_sf = sf;
  m_sync_words = sync_word;
  symbols_to_skip = 4;
  n_up = 8;

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
  message_port_register_in(pmt::mp("frame_info"));
  set_msg_handler(pmt::mp("frame_info"),
                  [this](pmt::pmt_t msg) { this->frame_info_handler(msg); });
  set_tag_propagation_policy(TPP_ONE_TO_ONE);

#ifdef GRLORA_MEASUREMENTS
  int num = 0; // check next file name to use
  while (1) {
    std::ifstream infile("../../matlab/measurements/sync" +
                         std::to_string(num) + ".txt");
    if (!infile.good())
      break;
    num++;
  }
  sync_log.open("../../matlab/measurements/sync" + std::to_string(num) + ".txt",
                std::ios::out | std::ios::trunc);
#endif
#ifdef GRLORA_DEBUGV
  numb_symbol_to_save = 80; // number of symbol per erroneous frame to save
  last_frame.resize(m_samples_per_symbol * numb_symbol_to_save);
  samples_file.open("../../matlab/err_symb.txt",
                    std::ios::out | std::ios::trunc);
#endif
#ifdef GRLORA_SAVE_PRE_DATA
  preamb_file.open("../../matlab/preambles/preamb.txt",
                   std::ios::out | std::ios::trunc);
  payload_file.open("../../matlab/data/data.txt",
                    std::ios::out | std::ios::trunc);
#endif
}

/*
 * Our virtual destructor.
 */
frame_sync_impl::~frame_sync_impl() {}

void frame_sync_impl::forecast(int noutput_items,
                               gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = usFactor * (m_samples_per_symbol + 2);
}

void frame_sync_impl::estimate_CFO(gr_complex *samples) {
  int k0;
  double Y_1, Y0, Y1, u, v, ka, wa, k_residual;
  std::vector<gr_complex> CFO_frac_correc_aug(
      up_symb_to_use * m_number_of_bins); ///< CFO frac correction vector
  std::vector<gr_complex> dechirped(up_symb_to_use * m_number_of_bins);
  kiss_fft_cpx *cx_in_cfo =
      new kiss_fft_cpx[2 * up_symb_to_use * m_samples_per_symbol];
  kiss_fft_cpx *cx_out_cfo =
      new kiss_fft_cpx[2 * up_symb_to_use * m_samples_per_symbol];

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
    } else { // add padding
      cx_in_cfo[i].r = 0;
      cx_in_cfo[i].i = 0;
    }
  }
  // do the FFT
  kiss_fft(cfg_cfo, cx_in_cfo, cx_out_cfo);
  // Get magnitude
  for (uint32_t i = 0u; i < 2 * up_symb_to_use * m_samples_per_symbol; i++) {
    fft_mag_sq[i] =
        cx_out_cfo[i].r * cx_out_cfo[i].r + cx_out_cfo[i].i * cx_out_cfo[i].i;
  }
  free(cfg_cfo);
  delete[] cx_in_cfo;
  delete[] cx_out_cfo;
  // get argmax here
  k0 = ((std::max_element(fft_mag_sq,
                          fft_mag_sq + 2 * up_symb_to_use * m_number_of_bins) -
         fft_mag_sq));

  // get three spectral lines
  Y_1 = fft_mag_sq[mod(k0 - 1, 2 * up_symb_to_use * m_number_of_bins)];
  Y0 = fft_mag_sq[k0];
  Y1 = fft_mag_sq[mod(k0 + 1, 2 * up_symb_to_use * m_number_of_bins)];
  // set constant coeff
  u = 64 * m_number_of_bins / 406.5506497; // from Cui yang (15)
  v = u * 2.4674;
  // RCTSL
  wa = (Y1 - Y_1) / (u * (Y1 + Y_1) + v * Y0);
  ka = wa * m_number_of_bins / M_PI;
  k_residual = fmod((k0 + ka) / 2 / up_symb_to_use, 1);
  lambda_cfo = k_residual - (k_residual > 0.5 ? 1 : 0);
  // Correct CFO in preamble
  for (int n = 0; n < up_symb_to_use * m_number_of_bins; n++) {
    CFO_frac_correc_aug[n] =
        gr_expj(-2 * M_PI * lambda_cfo / m_number_of_bins * n);
  }
  volk_32fc_x2_multiply_32fc(&preamble_up[0], samples, &CFO_frac_correc_aug[0],
                             up_symb_to_use * m_number_of_bins);
}
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
  delete[] cx_in_cfo;
  delete[] cx_out_cfo;
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

void frame_sync_impl::estimate_STO() {
  int k0;
  double Y_1, Y0, Y1, u, v, ka, wa, k_residual;

  std::vector<gr_complex> dechirped(m_number_of_bins);
  kiss_fft_cpx *cx_in_sto = new kiss_fft_cpx[2 * m_samples_per_symbol];
  kiss_fft_cpx *cx_out_sto = new kiss_fft_cpx[2 * m_samples_per_symbol];

  float fft_mag_sq[2 * m_number_of_bins];
  for (size_t i = 0; i < 2 * m_number_of_bins; i++) {
    fft_mag_sq[i] = 0;
  }
  kiss_fft_cfg cfg_sto = kiss_fft_alloc(2 * m_samples_per_symbol, 0, 0, 0);

  for (int i = 0; i < up_symb_to_use; i++) {
    // Dechirping
    volk_32fc_x2_multiply_32fc(&dechirped[0],
                               &preamble_up[m_number_of_bins * i],
                               &m_downchirp[0], m_samples_per_symbol);

    // prepare FFT
    for (int i = 0; i < 2 * m_samples_per_symbol; i++) {
      if (i < m_samples_per_symbol) {
        cx_in_sto[i].r = dechirped[i].real();
        cx_in_sto[i].i = dechirped[i].imag();
      } else { // add padding
        cx_in_sto[i].r = 0;
        cx_in_sto[i].i = 0;
      }
    }
    // do the FFT
    kiss_fft(cfg_sto, cx_in_sto, cx_out_sto);
    // Get magnitude
    for (uint32_t i = 0u; i < 2 * m_samples_per_symbol; i++) {

      fft_mag_sq[i] =
          cx_out_sto[i].r * cx_out_sto[i].r + cx_out_sto[i].i * cx_out_sto[i].i;
    }
  }
  free(cfg_sto);
  delete[] cx_in_sto;
  delete[] cx_out_sto;

  // get argmax here
  k0 = std::max_element(fft_mag_sq, fft_mag_sq + 2 * m_number_of_bins) -
       fft_mag_sq;

  // get three spectral lines
  Y_1 = fft_mag_sq[mod(k0 - 1, 2 * m_number_of_bins)];
  Y0 = fft_mag_sq[k0];
  Y1 = fft_mag_sq[mod(k0 + 1, 2 * m_number_of_bins)];
  // set constant coeff
  u = 64 * m_number_of_bins / 406.5506497; // from Cui yang (eq.15)
  v = u * 2.4674;
  // RCTSL
  wa = (Y1 - Y_1) / (u * (Y1 + Y_1) + v * Y0);
  ka = wa * m_number_of_bins / M_PI;
  k_residual = fmod((k0 + ka) / 2, 1);
  lambda_sto = k_residual - (k_residual > 0.5 ? 1 : 0);
}

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
  return sig_en ? ((std::max_element(fft_mag, fft_mag + m_number_of_bins) -
                    fft_mag))
                : -1;
}

float frame_sync_impl::determine_energy(const gr_complex *samples) {
  float magsq_chirp[m_samples_per_symbol];
  float energy_chirp = 0;
  volk_32fc_magnitude_squared_32f(magsq_chirp, samples, m_samples_per_symbol);
  volk_32f_accumulator_s32f(&energy_chirp, magsq_chirp, m_samples_per_symbol);
  return energy_chirp;
}

void frame_sync_impl::frame_info_handler(pmt::pmt_t frame_info) {
  pmt::pmt_t err = pmt::string_to_symbol("error");

  m_cr =
      pmt::to_long(pmt::dict_ref(frame_info, pmt::string_to_symbol("cr"), err));
  m_pay_len = pmt::to_double(
      pmt::dict_ref(frame_info, pmt::string_to_symbol("pay_len"), err));
  m_has_crc = pmt::to_long(
      pmt::dict_ref(frame_info, pmt::string_to_symbol("crc"), err));
  m_invalid_header = pmt::to_double(
      pmt::dict_ref(frame_info, pmt::string_to_symbol("err"), err));

  if (m_invalid_header) {
    m_state = DETECT;
    symbol_cnt = 1;
    k_hat = 0;
    lambda_sto = 0;
  } else {

    m_symb_numb = 8 + ceil((double)(2 * m_pay_len - m_sf + 2 +
                                    !m_impl_head * 5 + m_has_crc * 4) /
                           m_sf) *
                          (4 + m_cr);

    // std::cout<<"received_head_info: cr= "<<(int)m_cr<<" pay_len =
    // "<<(int)m_pay_len<<" crc = "<<(int)m_has_crc<< " err=
    // "<<(int)m_invalid_header<<" m_symb_numb = "<<(int)m_symb_numb<<std::endl;
    m_received_head = true;
    frame_info = pmt::dict_add(frame_info, pmt::intern("is_header"),
                               pmt::from_bool(false));
    add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_info"),
                 frame_info);
  }
}

int frame_sync_impl::general_work(int noutput_items,
                                  gr_vector_int &ninput_items,
                                  gr_vector_const_void_star &input_items,
                                  gr_vector_void_star &output_items) {
  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];
  int items_to_output = 0;
    //search for work_done tags and if found add them to the stream
    std::vector<tag_t> work_done_tags;
    get_tags_in_window(work_done_tags, 0, 0, ninput_items[0],
                       pmt::string_to_symbol("work_done"));
    if (work_done_tags.size()) {
        add_item_tag(0, nitems_written(0), pmt::intern("work_done"),
                     pmt::intern("done"), pmt::intern("frame_sync"));
        return 1;
    }
  // downsampling
  for (int ii = 0; ii < m_number_of_bins; ii++) {
      in_down[ii] =
              in[(int) (usFactor - 1 + usFactor * ii - round(lambda_sto * usFactor))];
  }
  switch (m_state) {
  case DETECT: {
    bin_idx_new = get_symbol_val(&in_down[0], &m_downchirp[0]);

    if (std::abs(bin_idx_new - bin_idx) <= 1 &&
        bin_idx_new != -1) { // look for consecutive reference upchirps(with a
                             // margin of ±1)
      if (symbol_cnt == 1) // we should also add the first symbol value
        k_hat += bin_idx;

      k_hat += bin_idx_new;
      memcpy(&preamble_raw[m_samples_per_symbol * symbol_cnt], &in_down[0],
             m_samples_per_symbol * sizeof(gr_complex));
      symbol_cnt++;
    } else {
      memcpy(&preamble_raw[0], &in_down[0],
             m_samples_per_symbol * sizeof(gr_complex));
      symbol_cnt = 1;
      k_hat = 0;
    }
    bin_idx = bin_idx_new;
    if (symbol_cnt == (int)(n_up - 1)) {
      m_state = SYNC;
      symbol_cnt = 0;
      cfo_sto_est = false;
      k_hat = round(k_hat / (n_up - 1));

      // perform the coarse synchronization
      items_to_consume = usFactor * (m_samples_per_symbol - k_hat);
    } else
      items_to_consume = usFactor * m_samples_per_symbol;
    items_to_output = 0;
    break;
  }
  case SYNC: {
    if (!cfo_sto_est) {
      estimate_CFO(&preamble_raw[m_number_of_bins - k_hat]);
      estimate_STO();
      // create correction vector
      for (int n = 0; n < m_number_of_bins; n++) {
        CFO_frac_correc[n] =
            gr_expj(-2 * M_PI * lambda_cfo / m_number_of_bins * n);
      }
      cfo_sto_est = true;
    }
    items_to_consume = usFactor * m_samples_per_symbol;
    // apply cfo correction
    volk_32fc_x2_multiply_32fc(&symb_corr[0], &in_down[0], &CFO_frac_correc[0],
                               m_samples_per_symbol);

    bin_idx = get_symbol_val(&symb_corr[0], &m_downchirp[0]);
    switch (symbol_cnt) {

    case NET_ID1: {

      if (bin_idx == 0 || bin_idx == 1 ||
          bin_idx == m_number_of_bins -
                         1) { // look for additional upchirps. Won't work if
                              // network identifier 1 equals 2^sf-1, 0 or 1!
      } else if (abs(bin_idx - (int32_t)m_sync_words[0]) >
                 1) { // wrong network identifier
        m_state = DETECT;
        symbol_cnt = 1;
        items_to_output = 0;
        k_hat = 0;
        lambda_sto = 0;
      } else { // network identifier 1 correct or off by one
        net_id_off = bin_idx - (int32_t)m_sync_words[0];
        symbol_cnt = NET_ID2;
      }
      break;
    }
    case NET_ID2: {
      if (abs(bin_idx - (int32_t)m_sync_words[1]) >
          1) { // wrong network identifier
        m_state = DETECT;
        symbol_cnt = 1;
        items_to_output = 0;
        k_hat = 0;
        lambda_sto = 0;
      } else if (net_id_off &&
                 (bin_idx - (int32_t)m_sync_words[1]) ==
                     net_id_off) { // correct case off by one net id
#ifdef GRLORA_MEASUREMENTS
        off_by_one_id = 1;
#endif

        items_to_consume -= usFactor * net_id_off;
        symbol_cnt = DOWNCHIRP1;
      } else {
#ifdef GRLORA_MEASUREMENTS
        off_by_one_id = 0;
#endif
        symbol_cnt = DOWNCHIRP1;
      }
      break;
    }
    case DOWNCHIRP1:
      symbol_cnt = DOWNCHIRP2;
      break;
    case DOWNCHIRP2: {
      down_val = get_symbol_val(&symb_corr[0], &m_upchirp[0]);
      symbol_cnt = QUARTER_DOWN;
      break;
    }
    case QUARTER_DOWN: {
#ifdef GRLORA_SAVE_PRE_DATA
      // save preamble
      for (int j = 0; j < 7; j++) {
        for (int i = 0; i < m_N; i++)
          preamb_file << preamble_raw[m_N - k_hat + i +
                                      m_N * j]
                             .real()
                      << (preamble_raw[m_N - k_hat + i +
                                       m_N * j]
                                      .imag() < 0
                              ? "-"
                              : "+")
                      << std::abs(preamble_raw[m_N - k_hat + i +
                                               m_N * j]
                                      .imag())
                      << "i,";
        preamb_file << std::endl;
      }
      std::cout << "saved one frame" << '\n';
#endif
      if (down_val < m_number_of_bins / 2) {
        CFOint = floor(down_val / 2);
        // message_port_pub(pmt::intern("new_frame"),pmt::mp((long)CFOint));

      } else {
        CFOint = ceil(double(down_val - (int)m_number_of_bins) / 2);

        CFOint = (m_number_of_bins + CFOint) % m_number_of_bins;
        // message_port_pub(pmt::intern("new_frame"),pmt::mp((long)((m_N+CFOint)%m_N)));
      }

      pmt::pmt_t frame_info = pmt::make_dict();
      frame_info = pmt::dict_add(frame_info, pmt::intern("is_header"),
                                 pmt::from_bool(true));
      frame_info = pmt::dict_add(frame_info, pmt::intern("cfo_int"),
                                 pmt::mp((long)CFOint));

      add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_info"),
                   frame_info);

      m_received_head = false;
      items_to_consume =
          usFactor * m_samples_per_symbol / 4 + usFactor * CFOint;
      symbol_cnt = 0;

      m_state = FRAC_CFO_CORREC;

#ifdef GRLORA_MEASUREMENTS
      sync_log << std::endl
               << lambda_cfo << ", " << lambda_sto << ", " << CFOint << ","
               << off_by_one_id << "," << lambda_bernier << ",";
#endif
    }
    }
    items_to_output = 0;
    break;
  }
  case FRAC_CFO_CORREC: {
    // transmitt only useful symbols (at least 8 symbol for PHY header)

    if (symbol_cnt < 8 || (symbol_cnt < m_symb_numb && m_received_head)) {
#ifdef GRLORA_SAVE_PRE_DATA
      // write data
      for (int i = 0; i < m_N; i++)
        payload_file << in_down[i].real() << (in_down[i].imag() < 0 ? "-" : "+")
                     << std::abs(in_down[i].imag()) << "i,";
      payload_file << std::endl;
#endif
      // apply fractional cfo correction
      volk_32fc_x2_multiply_32fc(out, &in_down[0], &CFO_frac_correc[0],
                                 m_samples_per_symbol);
#ifdef GRLORA_MEASUREMENTS
      sync_log << std::fixed << std::setprecision(10)
               << determine_energy(&in_down[0]) << ",";
#endif
#ifdef GRLORA_DEBUGV
      if (symbol_cnt < numb_symbol_to_save)
        memcpy(&last_frame[symbol_cnt * m_N], &in_down[0],
               m_samples_per_symbol * sizeof(gr_complex));
#endif
      items_to_consume = usFactor * m_samples_per_symbol;
      items_to_output = 1;
      symbol_cnt++;
    } else if (!m_received_head) { // Wait for the header to be decoded
      items_to_consume = 0;
      items_to_output = 0;
    } else {
      m_state = DETECT;
      symbol_cnt = 1;
      items_to_consume = usFactor * m_samples_per_symbol;
      items_to_output = 0;
      k_hat = 0;
      lambda_sto = 0;
    }
    break;
  }
  default: {
    std::cerr << "[LoRa sync] WARNING : No state! Shouldn't happen\n";
    break;
  }
  }
  consume_each(items_to_consume);
  // std::cout<<" items_to_consume "<<items_to_consume<<", noutput_items
  // "<<noutput_items<<", items_to_output "<<items_to_output<<std::endl;
  return items_to_output;
}
} /* namespace lora_sdr */
} /* namespace gr */
