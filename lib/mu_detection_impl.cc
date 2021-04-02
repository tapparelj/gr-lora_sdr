/* -*- c++ -*- */
/*
 * Copyright 2020 Joachim Tapparel TCL@EPFL.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "mu_detection_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

mu_detection::sptr mu_detection::make(uint8_t sf, uint8_t os_factor,
                                      int snr_threshold) {
  return gnuradio::get_initial_sptr(
      new mu_detection_impl(sf, os_factor, snr_threshold));
}

/**
 * @brief Construct a new mu detection impl::mu detection impl object
 * 
 * @param sf 
 * @param os_factor 
 * @param snr_threshold 
 */
mu_detection_impl::mu_detection_impl(uint8_t sf, uint8_t os_factor,
                                     int snr_threshold)
    : gr::block("mu_detection",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {
  m_sf = sf;
  m_n_up = 8;
  m_os_factor = os_factor;
  m_N = (uint32_t)(1u << m_sf);

  m_snr_threshold = snr_threshold; // in dB
  m_L_threshold = 0.90;

  m_wait_one_symb = false;
  m_ignore_next = false;

  m_power_avg = 0;
  m_noise_est = 1;

  m_samples_per_symbol = (uint32_t)(1u << m_sf) * m_os_factor;

  m_preamble.resize((int)m_samples_per_symbol * (m_n_up + 2 + 2.25 + 2), 0);
  m_matched_filter.resize(2 * m_samples_per_symbol);
  m_deci_preamb_down.resize((1 + 2.25) * m_N);
  m_deci_preamb_up.resize(m_N);
  m_mf_conv_out.resize(1.25 * (m_samples_per_symbol / m_os_factor));
  m_mf_conv_out_abs.resize(m_os_factor, std::vector<float>((int)(m_N * 1.25)));

  m_dfts.resize(m_n_up - 1, std::vector<gr_complex>(m_N, 0));
  m_dfts_mag.resize(m_n_up - 1, std::vector<float>(m_N, 0));
  m_dft_mag_prod.resize(m_N, 0);

#ifdef GRLORA_DEBUG
  out_file.open("../../matlab/debug/detect.txt",
                std::ios::out | std::ios::trunc);
  m_matched_filter_en = 0;
#endif

  m_downchirp.resize(m_N);

  double sum = 0;
  for (uint n = 0; n < m_N; n++) {
    m_downchirp[n] = gr_expj(-2.0 * M_PI * (pow(n, 2) / (2 * m_N) - 0.5 * n));
  }

  message_port_register_in(pmt::mp("noise_est"));
  // set_msg_handler(pmt::mp("noise_est"),boost::bind(&mu_detection_impl::noise_handler,
  // this, _1));
  set_msg_handler(pmt::mp("noise_est"),
                  [this](pmt::pmt_t msg) { this->noise_handler(msg); });
}

/**
 * @brief Destroy the mu detection impl::mu detection impl object
 * 
 */
mu_detection_impl::~mu_detection_impl() {}

/**
 * @brief 
 * 
 * @param noutput_items 
 * @param ninput_items_required 
 */
void mu_detection_impl::forecast(int noutput_items,
                                 gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = m_samples_per_symbol;
}

/**
 * @brief 
 * 
 * @param noise_est 
 */
void mu_detection_impl::noise_handler(pmt::pmt_t noise_est) {
  std::cout << "[mu_detection_impl.cc] Noise estimation received: "
            << pmt::to_double(noise_est) << '\n';
  m_noise_est = pmt::to_double(noise_est);
}

/**
 * @brief 
 * 
 * @param input_symb 
 */
void mu_detection_impl::add_user_tag(int input_symb) {
  pmt::pmt_t user_tag = pmt::make_dict();

  user_tag = pmt::dict_add(user_tag, pmt::intern("power"),
                           pmt::from_double(m_param.power));
  user_tag = pmt::dict_add(user_tag, pmt::intern("sto_frac"),
                           pmt::from_double(m_param.sto_frac));
  user_tag = pmt::dict_add(user_tag, pmt::intern("sto_int"),
                           pmt::from_long(m_param.sto_int));
  user_tag = pmt::dict_add(user_tag, pmt::intern("cfo_frac"),
                           pmt::from_double(m_param.cfo_frac));
  user_tag = pmt::dict_add(user_tag, pmt::intern("cfo_int"),
                           pmt::from_long(m_param.cfo_int));
  add_item_tag(
      0,
      nitems_written(0) + m_os_factor * m_N + (m_param.sto_int * m_os_factor) +
          m_param.sto_frac * (m_os_factor) + m_samples_per_symbol * input_symb,
      pmt::string_to_symbol("new_user"), user_tag);
  std::cout << "[mu_detection_impl.cc] "
            << " offset "
            << nitems_written(0) + m_os_factor * m_N +
                   (m_param.sto_int * m_os_factor) +
                   m_param.sto_frac * (m_os_factor) +
                   m_samples_per_symbol * input_symb
            << " user found: power= " << m_param.power
            << ", SNR= " << m_param.snr << ", sto_int= " << m_param.sto_int
            << ", sto_frac= " << m_param.sto_frac
            << ", cfo_int= " << m_param.cfo_int
            << ", cfo_frac= " << m_param.cfo_frac << ", s_up= " << m_param.s_up
            << ", s_down= " << m_param.s_down << '\n';
}

/**
 * @brief 
 * 
 * @param delay 
 */
void mu_detection_impl::estimate_CFO_frac(int delay = 0) {

  std::vector<gr_complex> dechirped(m_N);
  std::vector<float>::iterator max_it;

  if (!delay) {

    kiss_fft_cpx *cx_in_cfo = new kiss_fft_cpx[m_N];
    kiss_fft_cpx *cx_out_cfo = new kiss_fft_cpx[m_N];
    kiss_fft_cfg cfg_cfo = kiss_fft_alloc(m_N, 0, 0, 0);

    // downsample the m_n_up symbol(new upchirp) with a stride of m_os_factor
    for (size_t i = 0; i < m_N; i++) {
      m_deci_preamb_up[i] =
          m_preamble[(m_n_up - 1) * m_samples_per_symbol + m_os_factor * i];
    }

    // dechirp the new potential upchirp
    volk_32fc_x2_multiply_32fc(&dechirped[0], &m_deci_preamb_up[0],
                               &m_downchirp[0], m_N);

    // get the DFT of the new potential upchirp
    for (int i = 0; i < m_N; i++) {
      cx_in_cfo[i].r = dechirped[i].real();
      cx_in_cfo[i].i = dechirped[i].imag();
    }

    // do the FFT
    kiss_fft(cfg_cfo, cx_in_cfo, cx_out_cfo);

    // store new fft with the m_n_up-2 previous
    std::rotate(m_dfts.begin(), m_dfts.begin() + 1, m_dfts.end());
    memcpy(&m_dfts[m_n_up - 2][0], &cx_out_cfo[0], m_N * sizeof(gr_complex));

    // Get and store magnitude
    std::rotate(m_dfts_mag.begin(), m_dfts_mag.begin() + 1, m_dfts_mag.end());
    for (int i = 0; i < m_N; i++) {
      m_dfts_mag[m_n_up - 2][i] = std::sqrt(cx_out_cfo[i].r * cx_out_cfo[i].r +
                                            cx_out_cfo[i].i * cx_out_cfo[i].i);
    }
    // get the argmax of this fft
    max_it = std::max_element(m_dfts_mag[m_n_up - 2].begin(),
                              m_dfts_mag[m_n_up - 2].end());
    int argmax = std::distance(m_dfts_mag[m_n_up - 2].begin(), max_it);

    // multiply the dfts of the last 6 potential upchirps with the new one.
    std::fill(m_dft_mag_prod.begin(), m_dft_mag_prod.end(), 1.0);

    for (int i = 0; i < m_n_up - 1; i++) {
      volk_32f_x2_multiply_32f(&m_dft_mag_prod[0], &m_dft_mag_prod[0],
                               &m_dfts_mag[i][0], m_N);
    }

    // get argmax to estimate the main bin (S_up)
    max_it = std::max_element(m_dft_mag_prod.begin(), m_dft_mag_prod.end());
    m_param.s_up = std::distance(m_dft_mag_prod.begin(), max_it);
    m_prod_max_mag = *max_it;
    // std::cout <<"max: "<<*max_it<<" at :"<<param.s_up <<'\n';

    m_power_avg = m_power_avg * 7 / 8 + m_dfts_mag[m_n_up - 2][argmax] * 1 / 8;

    free(cfg_cfo);
    delete[] cx_in_cfo;
    delete[] cx_out_cfo;
  }
  // multiply complex conjugate of symbol n with symbol n+1 and cumulate
  gr_complex m_cumul = 0;
  int side_peaks = 0;

  for (size_t i = -1 * side_peaks; i <= side_peaks;
       i++) { // take more peak of each side of the max
    for (size_t j = 0 + delay; j < m_n_up - 2; j++) {
      m_cumul += std::conj(m_dfts[j][mod(m_param.s_up + i, m_N)]) *
                 m_dfts[j + 1][mod(m_param.s_up + i, m_N)];
    }
  }

  m_param.cfo_frac = std::arg(m_cumul) / (2 * M_PI);
  return;
}

/**
 * @brief 
 * 
 * @param noutput_items 
 * @param ninput_items 
 * @param input_items 
 * @param output_items 
 * @return int 
 */
int mu_detection_impl::general_work(int noutput_items,
                                    gr_vector_int &ninput_items,
                                    gr_vector_const_void_star &input_items,
                                    gr_vector_void_star &output_items) {

  if (m_init) {
    m_init = false;
    gr::thread::thread_bind_to_processor(7);

#ifdef THREAD_MEASURE
    const pid_t tid = syscall(SYS_gettid);
    setpriority(PRIO_PROCESS, tid, 2);
#endif
    m_init = true;
  }

  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];

  std::vector<gr_complex> in_cfo(m_samples_per_symbol);
  std::vector<float>::iterator max_it;
  int n_input_symb = std::min(ninput_items[0] / m_samples_per_symbol,
                              noutput_items / m_samples_per_symbol);

  for (int input_symb = 0; input_symb < n_input_symb; input_symb++) {
    //   copy one symbol to the output
    memcpy(&out[m_samples_per_symbol * input_symb], &m_preamble[0],
           m_samples_per_symbol * sizeof(gr_complex));

    // shift left rest of the buffer
    std::rotate(m_preamble.begin(), m_preamble.begin() + m_samples_per_symbol,
                m_preamble.end());

    // add newly received symbol to the preamble buffer
    memcpy(&m_preamble[m_samples_per_symbol * (m_n_up + 2 + 2.25 + 1)],
           &in[m_samples_per_symbol * input_symb],
           m_samples_per_symbol * sizeof(gr_complex));

    // estimate cfo and S_up using the symbols 1 to 7 of the preamble (avoid
    // first one as might be partially noise)
    estimate_CFO_frac();

    // get the new matched filter corresponding to the estimated cfo_frac
    for (uint n = 0; n < 2 * m_N; n++) {
      m_matched_filter[n] = gr_expj(2 * M_PI *
                                    (pow(n, 2) / (2 * m_N) - 0.5 * n -
                                     m_param.cfo_frac * n / (double)m_N));
    }

    // Detect downchirp and estimate S_down
    std::vector<float> max(m_os_factor);
    std::vector<int> argmax(m_os_factor);

    for (size_t i = 0; i < m_os_factor; i++) {

      // decimate m_preamble[m_os_factor*m_samples_per_symbol*(m_n_up+2)+i] by
      // m_os_factor
      for (size_t j = 0; j < m_N * (3.25); j++) {
        m_deci_preamb_down[j] =
            m_preamble[m_os_factor * (m_N * (m_n_up + 2) + j) + i];
      }
      // convolve the match filter with the decimated preamble

      m_mf_conv_out.resize(m_N * 1.25);
      for (size_t j = 0; j < 1.25 * m_N; j++) {
        volk_32fc_x2_dot_prod_32fc(&m_mf_conv_out[j], &m_deci_preamb_down[j],
                                   &m_matched_filter[0], m_N * 2);
        m_mf_conv_out_abs[i][j] = std::abs(m_mf_conv_out[j]);
      }

#ifdef GRLORA_DEBUG
      for (size_t j = 0; j < m_mf_conv_out.size(); j++) {
        out_file << m_mf_conv_out[j].real()
                 << (m_mf_conv_out[j].imag() < 0 ? "-" : "+")
                 << std::abs(m_mf_conv_out[j].imag()) << "i,";
      }
      out_file << "\n";
#endif

      // get argmax of the convolution
      max_it = std::max_element(m_mf_conv_out_abs[i].begin(),
                                m_mf_conv_out_abs[i].end());
      argmax[i] = std::distance(m_mf_conv_out_abs[i].begin(), max_it);

      max[i] = *max_it;
    }
    // find the best phase to use
    max_it = std::max_element(max.begin(), max.end());
    m_param.s_down = argmax[std::distance(max.begin(), max_it)];
    m_param.sto_frac =
        (double)std::distance(max.begin(), max_it) / (m_os_factor);

    if (m_param.sto_frac >= 0.5)
      m_param.s_up = mod(m_param.s_up + 1, m_N);
    // estimate POWER
    m_param.power = pow(*max_it / (1u << (m_sf + 1)), 2);

    // new user detection

    float L_prev, L_next = 0;
    gr_complex ml_prev, ml_next = 0;
    std::vector<gr_complex> prev_downchirp(2 * m_N, 0);
    std::vector<gr_complex> next_downchirp(2 * m_N, 0);

    bool user_detected = false;

    // compare magnitude of the new max bin with the one N*os_factor samples
    // before
    if (m_param.s_down >= m_N) {
      // half peak is N samples before in the same vector
      ml_prev = m_mf_conv_out_abs[m_param.sto_frac * m_os_factor]
                                 [m_param.s_down - m_N];
    } else {
      // get the maximum likelihood of the half peak. (N*os_factor before the
      // main peak)

      for (size_t ii = 0; ii < m_N * 2; ii++) {
        // samples of interest start at m_N*(m_n_up+1) + the postition of
        // interest(s_down) and you want the phase of interest
        // (sto_frac*os_factor)
        prev_downchirp[ii] = m_preamble[m_os_factor * (m_N * (m_n_up + 1) + ii +
                                                       m_param.s_down) +
                                        m_param.sto_frac * m_os_factor];
      }
      volk_32fc_x2_dot_prod_32fc(&ml_prev, &prev_downchirp[0],
                                 &m_matched_filter[0], m_N * 2);
    }
    L_prev = std::abs(std::abs(ml_prev) / m_N - sqrt(m_param.power)) /
             sqrt(m_param.power) / sqrt(m_noise_est / m_N + 2 / M_PI);

    // compare the magnitude of the new bin with the next one (N samples after)
    if (m_param.s_down < m_N / 4) {
      ml_next = m_mf_conv_out_abs[m_param.sto_frac * m_os_factor]
                                 [m_param.s_down + m_N];
    } else {
      for (size_t ii = 0; ii < m_N * 2; ii++) {
        // samples of interest start at m_N*(m_n_up+1) + the postition of
        // interest(s_down) and you want the phase of interest
        // (sto_frac*os_factor)
        next_downchirp[ii] = m_preamble[m_os_factor * (m_N * (m_n_up + 3) + ii +
                                                       m_param.s_down) +
                                        m_param.sto_frac * m_os_factor];
      }
      volk_32fc_x2_dot_prod_32fc(&ml_next, &next_downchirp[0],
                                 &m_matched_filter[0], m_N * 2);
    }
    L_next = std::abs(std::abs(ml_next) / m_N - sqrt(m_param.power)) /
             sqrt(m_param.power) / sqrt(m_noise_est / m_N + 2 / M_PI);

    // Estimate SNR of the user
    m_param.snr = 10 * log10(m_param.power / m_noise_est);

    bool is_not_payload = m_prod_max_mag > pow(.9 * m_power_avg, 7);
    bool peak_centered = (L_prev < m_L_threshold) && (L_next < m_L_threshold);
    bool snr_sufficient = m_param.snr > m_snr_threshold;

    if (is_not_payload && peak_centered && snr_sufficient) {
      user_detected = true;
    }

    if (m_wait_one_symb && !user_detected) {
      add_user_tag(input_symb);
      m_ignore_next = true;
      m_wait_one_symb = false;
    } else if (!m_ignore_next && user_detected) {
      // get sto_int and cfo_int
      m_param.cfo_int = mod(m_param.s_up + m_param.s_down, m_N);
      if (m_param.cfo_int >= m_N / 2)
        m_param.cfo_int = ceil(m_param.cfo_int - (int)m_N) / 2.0;
      else
        m_param.cfo_int = ceil(m_param.cfo_int / 2.0);

      m_param.sto_int = mod((int)m_N - m_param.s_up + m_param.cfo_int, m_N);

      if (m_param.s_down >=
          m_N) { // a better approx of cfo_frac might appear in m_N samples
        if (m_param.sto_int + m_param.cfo_int < m_N) {
          m_wait_one_symb = true;
        } else {
          add_user_tag(input_symb);
          m_ignore_next = true;
        }

      }
      // the n_up upchirps are currently used to estimate the cfo and will
      // reapear in the next iteration but must me ignored
      else if (m_param.sto_int + m_param.cfo_int <= 0 && !m_wait_one_symb) {
        estimate_CFO_frac(1);

        add_user_tag(input_symb + 1);
        m_ignore_next = true;

      } else {
        add_user_tag(input_symb);
        m_ignore_next = true;
        m_wait_one_symb = false;
      }
    } else if (m_ignore_next)
      m_ignore_next = false;
#ifdef GRLORA_DEBUG
    if (m_matched_filter_en) {
      m_matched_filter_en--;

      if (!m_matched_filter_en)
        std::cout << "[mu_detection_impl.cc] "
                  << "match filter disabled"
                  << "\n";
    }
#endif
  }
  consume_each(m_samples_per_symbol * n_input_symb);

  // Tell runtime system how many output items we produced.

  return m_samples_per_symbol * n_input_symb;
}

} /* namespace lora_sdr */
} /* namespace gr */
