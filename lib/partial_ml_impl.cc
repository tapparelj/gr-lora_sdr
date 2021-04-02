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

#include "partial_ml_impl.h"
#include <boost/math/special_functions/bessel.hpp>
#include <chrono>
#include <gnuradio/io_signature.h>
#include <sys/resource.h>
#include <sys/syscall.h>

bool cmp_mags(const std::tuple<int, double, double> &a,
              const std::tuple<int, double, double> &b) {
  return std::get<1>(a) > std::get<1>(b); // decreasing order
}

namespace gr {
namespace lora_sdr {

partial_ml::sptr partial_ml::make(uint8_t sf, uint8_t id) {
  return gnuradio::get_initial_sptr(new partial_ml_impl(sf, id));
}

/**
 * @brief Construct a new partial ml impl::partial ml impl object
 *
 * @param sf
 * @param id
 */
partial_ml_impl::partial_ml_impl(uint8_t sf, uint8_t id)
    : gr::block("partial_ml", gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make3(3, 3, sizeof(float),
                                        sizeof(gr_complex) * (1u << sf),
                                        sizeof(gr_complex) * (1u << sf))) {
  m_init = false;

  m_sf = sf;
  m_id = id;

  m_N = (uint32_t)(1u << m_sf);
  m_Ki = m_N;

  set_tag_propagation_policy(TPP_DONT);

  third_symbol_part.resize(m_Ki, false);

  prev_theta_u = 0;
  first_upchirp = true;

  m_ref_upchirp.resize(m_N);
  m_ref_downchirp.resize(m_N);
  mf.resize(m_N);

  for (uint n = 0; n < m_N; n++) {
    m_ref_upchirp[n] = gr_expj(2.0 * M_PI * (pow(n, 2) / (2 * m_N) - 0.5 * n));
  }

  volk_32fc_conjugate_32fc(&m_ref_downchirp[0], &m_ref_upchirp[0], m_N);
  Su = 0;
  theta_u = 0;
  Mu = 0;
  SNR_est = 0.0;

#ifdef GRLORA_DEBUG
  if (!m_id)
    out_file.open("../../matlab/debug/partial_debug.txt",
                  std::ios::out | std::ios::trunc);
#endif
}

/**
 * @brief Destroy the partial ml impl::partial ml impl object
 * 
 */
partial_ml_impl::~partial_ml_impl() {}

/**
 * @brief 
 * 
 * @param noutput_items 
 * @param ninput_items_required 
 */
void partial_ml_impl::forecast(int noutput_items,
                               gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = m_N;
}

/**
 * @brief 
 * 
 * @param Su 
 * @param Si1 
 * @param Si2 
 * @param Mu 
 * @param Mi1 
 * @param Mi2 
 * @param SNR_est 
 */
void partial_ml_impl::add_demod_tag(int Su, int Si1, int Si2, double Mu,
                                    double Mi1, double Mi2, double SNR_est) {
  // Create and add tag with demodulated symbols & likelihoods
  pmt::pmt_t demod_tag = pmt::make_dict();

  demod_tag = pmt::dict_add(demod_tag, pmt::intern("Su"), pmt::from_long(Su));
  demod_tag = pmt::dict_add(demod_tag, pmt::intern("Si1"), pmt::from_long(Si1));
  demod_tag = pmt::dict_add(demod_tag, pmt::intern("Si2"), pmt::from_long(Si2));

  demod_tag = pmt::dict_add(demod_tag, pmt::intern("Mu"), pmt::from_double(Mu));
  demod_tag =
      pmt::dict_add(demod_tag, pmt::intern("Mi1"), pmt::from_double(Mi1));
  demod_tag =
      pmt::dict_add(demod_tag, pmt::intern("Mi2"), pmt::from_double(Mi2));

  demod_tag =
      pmt::dict_add(demod_tag, pmt::intern("SNR"), pmt::from_double(SNR_est));

  add_item_tag(0, nitems_written(0), pmt::string_to_symbol("partial_ml"),
               demod_tag);
}

inline bool partial_ml_impl::is_kind_upchirp(long t) {
  return (t == UPCHIRP || t == SYNC_WORD || t == PAYLOAD);
}

inline bool partial_ml_impl::is_kind_downchirp(long t) {
  return (t == DOWNCHIRP || t == QUARTER_DOWN);
}
/**
 * @brief 
 * 
 * @param samples 
 * @param type 
 * @return std::vector<std::tuple<int, double, double>> 
 */
std::vector<std::tuple<int, double, double>>
partial_ml_impl::dechirp_and_fft(const gr_complex *samples, Symbol_type type) {
  // dechirp
  std::vector<gr_complex> dechirped(window.win_len);
  std::vector<std::tuple<int, double, double>> dft_out(m_N);

  if (type == DOWNCHIRP || type == QUARTER_DOWN)
    volk_32fc_x2_multiply_32fc(&dechirped[0], &samples[0], &m_ref_upchirp[0],
                               window.win_len);
  else
    volk_32fc_x2_multiply_32fc(&dechirped[0], &samples[0], &m_ref_downchirp[0],
                               window.win_len);

  // init for fft
  kiss_fft_cpx *cx_in = new kiss_fft_cpx[window.win_len];
  kiss_fft_cpx *cx_out = new kiss_fft_cpx[window.win_len];
  kiss_fft_cfg cfg = kiss_fft_alloc(window.win_len, 0, 0, 0);

  for (int i = 0; i < window.win_len; i++) {
    cx_in[i].r = dechirped[i].real();
    cx_in[i].i = dechirped[i].imag();
  }

  // do the FFT
  kiss_fft(cfg, cx_in, cx_out);

  // compute the magnitudes
  for (int i = 0; i < window.win_len; i++) {
    double mag_i =
        std::sqrt(cx_out[i].r * cx_out[i].r + cx_out[i].i * cx_out[i].i);
    double phase_i = std::atan2(cx_out[i].i, cx_out[i].r);
    dft_out[i] = std::tuple<int, double, double>(i, mag_i, phase_i);
  }
  for (int i = window.win_len; i < m_N; i++) {
    double mag_i = 0;
    double phase_i = 0;
    dft_out[i] = std::tuple<int, double, double>(i, mag_i, phase_i);
  }

  free(cfg);
  delete[] cx_in;
  delete[] cx_out;

  return dft_out;
}

/**
 * @brief 
 * 
 * @param dechirped 
 * @param win_len 
 * @param Si 
 * @param tau 
 * @param delta_cfo 
 * @param win_type 
 * @return gr_complex 
 */
gr_complex partial_ml_impl::matched_filter1(const gr_complex *dechirped,
                                            int win_len, int Si, double tau,
                                            double delta_cfo, int win_type) {
  int32_t ctau = ceil(tau);
  uint32_t mf_len = 0;
  double angle_corr = 0;

  if (win_len == m_N || (win_len == m_N / 4 && win_type == QUARTER_DOWN)) {
    mf_len = std::min(ctau, win_len);
  } else {
    mf_len = win_len;
  }
  // we need to take the case where a symbol is recovered from 3 parts (instead
  // of two)
  // in that case we need to apply a phase correction depending on the change of
  // ctau for the third symbol part
  if (third_symbol_part[Si]) {
    angle_corr = std::arg(m_ref_downchirp[mod((ctau - m_N / 4), m_N)]) -
                 std::arg(m_ref_downchirp[ctau]);

    third_symbol_part[Si] = false;
  }

  for (int n = 0; n < mf_len; n++) {
    double ph = (Si - tau + delta_cfo) * (n + m_N - ctau) / m_N;
    if ((n >= ctau - Si))
      ph += tau;

    mf[n] = gr_expj(-2.0 * M_PI * ph - angle_corr);
  }

  volk_32fc_x2_multiply_32fc(&mf[0], &dechirped[0], &mf[0], mf_len);

  gr_complex mf_acc = 0;
  for (uint n = 0; n < mf_len; n++) {
    mf_acc += mf[n];
  }

  if (win_len == m_N / 4 && win_type == QUARTER_DOWN && ctau >= win_len) {
    third_symbol_part[Si] = true;
  }

  return mf_acc / (float)m_N;
}

/**
 * @brief 
 * 
 * @param dechirped 
 * @param win_len 
 * @param Si 
 * @param tau 
 * @param delta_cfo 
 * @param win_type 
 * @return gr_complex 
 */
gr_complex partial_ml_impl::matched_filter2(const gr_complex *dechirped,
                                            int win_len, int Si, double tau,
                                            double delta_cfo, int win_type) {

  uint32_t ctau = ceil(tau);
  uint32_t mf_len = 0;
  uint32_t first_sample = 0;
  double ph;
  double angle_corr = 0;

  if (win_len == m_N) {
    mf_len = std::max(0, win_len - (int)ctau);
    first_sample = ctau;
  } else if (win_len == m_N / 4 && win_type == QUARTER_DOWN) {
    mf_len = std::max(0, win_len - (int)ctau);
    first_sample = ctau;
    // we need to apply a correction to the phase of the match filter since the
    // phase of the downchirp used to dechirp the symbol is not the same for
    // the symbol part in Mi1 and in Mi2.
    angle_corr = std::arg(m_ref_downchirp[mod((ctau - m_N / 4), m_N)]) -
                 std::arg(m_ref_downchirp[ctau]);
  } else {
    mf_len = win_len;
    first_sample = 0;
  }

  for (uint n = 0; n < mf_len; n++) {

    ph = (Si - tau + delta_cfo) * n / m_N;

    if (n >= m_N - Si)
      ph += tau;

    mf[n] = gr_expj(-2.0 * M_PI * ph + angle_corr);
  }
  volk_32fc_x2_multiply_32fc(&mf[0], &dechirped[first_sample], &mf[0], mf_len);

  gr_complex mf_acc = 0;
  for (uint n = 0; n < mf_len; n++) {
    mf_acc += mf[n];
  }
  return mf_acc / (float)m_N;
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
int partial_ml_impl::general_work(int noutput_items,
                                  gr_vector_int &ninput_items,
                                  gr_vector_const_void_star &input_items,
                                  gr_vector_void_star &output_items) {
  if (!m_init) {
    gr::thread::thread_bind_to_processor(m_id);
#ifdef THREAD_MEASURE
    const pid_t tid = syscall(SYS_gettid);
    setpriority(PRIO_PROCESS, tid, 4);
#endif
    m_init = true;
  }
  if (noutput_items >= 1) {

    const gr_complex *in = (const gr_complex *)input_items[0];
    float *out_L = (float *)output_items[0];
    float *out_Mi1 = (float *)output_items[1];
    float *out_Mi2 = (float *)output_items[2];

    int Si1 = 0;
    int Si2 = 0;

    std::vector<gr_complex> Mi1, Mi2;
    Mi1.resize(m_N, 0);
    Mi2.resize(m_N, 0);

    std::vector<tag_t> tags;
    get_tags_in_window(tags, 0, 0, 1, pmt::string_to_symbol("new_window"));
    if (tags.size() !=
        1) { // no tag found, we just consume 1 sample, but should not happen
      std::cerr << RED << "[partial_ml.cc] ERROR: no tag found on first sample!"
                << RESET << std::endl;
      consume_each(1);
      return 0;
    }
    tag_t win_tag = tags[0];
    pmt::pmt_t err =
        pmt::string_to_symbol("Error when parsing 'new_window' tag.");

    window.power1 = pmt::to_double(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("power1"), err));
    window.power2 = pmt::to_double(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("power2"), err));
    window.win_len = pmt::to_long(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("win_len"), err));
    window.Tu = pmt::to_long(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("Tu"), err));
    window.Ti1 = pmt::to_long(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("Ti1"), err));
    window.Ti2 = pmt::to_long(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("Ti2"), err));
    window.tau = pmt::to_double(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("tau"), err));
    window.delta_cfo = pmt::to_double(
        pmt::dict_ref(win_tag.value, pmt::string_to_symbol("delta_cfo"), err));

    // copying window tag to L output
    win_tag.offset = nitems_written(0);
    if (m_id == 0)
      add_item_tag(0, win_tag);

    // attribute powers
    float Pu = std::max(window.power1, window.power2);
    float Pi = std::min(window.power1, window.power2);

    int Su_nc = 0;

    if (window.Tu != VOID && window.Tu != QUARTER_DOWN) {
      // dechirp the window and do the fft
      std::vector<std::tuple<int, double, double>> fft_out =
          dechirp_and_fft(&in[0], (Symbol_type)window.Tu);

      // sort vector by decreasing order of magnitudes
      std::vector<std::tuple<int, double, double>> fft_sorted(fft_out);
      std::sort(fft_sorted.begin(), fft_sorted.end(), cmp_mags);

      // get candidate Su with its likelihood and phase
      std::tuple<int, double, double> bin_u = fft_sorted[m_id];

      Su = std::get<0>(bin_u);
      Mu = std::get<1>(bin_u) / m_N;
      theta_u = std::get<2>(bin_u);

      // for (int i = 0; i < fft_out.size(); i++)
      // {
      //     out_file<<std::get<1>(fft_out[i])<<",";
      // }
      // out_file<<std::endl;

      // //-------------COHERENT DEMOD Single user START
      // float max_val = 0;
      // float tmp_val = 0;
      // // For first upchirp, we don't have a prev_theta_u. We need to use the
      // non-coherent main bin

      // if(window.Tu == UPCHIRP && first_upchirp){
      //     first_upchirp = false;
      //     Su = std::get<0>(bin_u);
      //     Mu = std::get<1>(bin_u)/m_N;
      //     theta_u = std::get<2>(bin_u);
      // }
      // else{
      //     for(int i = 0; i<m_N;i++){
      //         // tmp_val = std::real(std::polar(std::get<1>(fft_out[i]),
      //         std::get<2>(fft_out[i]) - prev_theta_u)); tmp_val =
      //         std::real(gr_complex(std::get<1>(fft_out[i]),0.0)*gr_expj(std::get<2>(fft_out[i])
      //         - prev_theta_u)); if(tmp_val>max_val){
      //             Su = i;
      //             Mu = tmp_val;
      //             theta_u = std::get<2>(fft_out[i]);
      //             max_val = tmp_val;
      //         }
      //     }
      // }

      // if(window.Tu == PAYLOAD){
      //     first_upchirp = true;
      // }
      // // if(Su != Su_nc && window.Tu == PAYLOAD ){
      // //     std::cout<<"Su non-coh= "<<Su_nc<<" Su coh= "<<Su_coh<<" maxval=
      // "<<max_val<<std::endl;
      // // }

      // static gr_complex preamb_peak_cum; //TODO modify as nice bug source
      // // // save fft
      // // for(int i=0;i<fft_out.size();i++){
      // //     out_file<<
      // std::get<1>(fft_out[i])<<","<<std::get<2>(fft_out[i])<<",";
      // // }
      // // out_file<<std::arg(preamb_peak_cum)<<","<<prev_theta_u<<std::endl;

      // if (window.Tu == UPCHIRP && preamb_peak.size() == 8){
      // //reset preamb phase est
      // preamb_peak.clear();
      // }
      // if(window.Tu == UPCHIRP ){
      //     // std::cout<<"upchirp with phase: "<<theta_u<<std::endl;
      //     preamb_peak.push_back((gr_complex)std::polar(Mu,theta_u));
      // }

      // if(preamb_peak.size() == 8){//we have seen all the upchirps
      //     preamb_peak_cum = 0;
      //     float preamb_peak_avg=0;
      //     for(int i=0;i<8;i++){
      //         preamb_peak_cum += preamb_peak[i];
      //         preamb_peak_avg += std::arg(preamb_peak[i]);
      //     }
      //     // std::cout<<"avg phase: "<<std::arg(preamb_peak_cum);

      // }
      // prev_theta_u = theta_u;

      // //-------------COHERENT DEMOD END

      // estimate SNR
      double noise_energy = 0.0;
      double signal_energy = 0.0;

      for (int i = 0; i < m_N; i++) {
        double energy_i = pow(std::get<1>(fft_out[i]), 2);
        if (mod(std::abs(i - Su), m_N - 1) <
            2) // set to 2take three bins aside to consider cases with bad
               // cfo/sto estimation.(energy not in a single bin)
          signal_energy += energy_i;
        else
          noise_energy += energy_i;
      }

      SNR_est = signal_energy / noise_energy;
    }

    double Lu = boost::math::cyl_bessel_i(0, std::sqrt(Pu) * Mu / Pu);

    if ((window.Ti1 == VOID || window.Ti1 == DOWNCHIRP ||
         window.Ti1 == QUARTER_DOWN) &&
        (window.Ti2 == VOID || window.Ti2 == DOWNCHIRP ||
         window.Ti2 == QUARTER_DOWN)) {
      // single user case, we're done

      consume_each(window.win_len);

      add_demod_tag(Su, 0, 0, Mu, 0.0, 0.0, SNR_est);

      out_L[0] = Lu;
      memset(&out_Mi1[0], 0, sizeof(gr_complex) * m_N);
      memset(&out_Mi2[0], 0, sizeof(gr_complex) * m_N);
      return 1;
    }
    // Removing the strongest user
    std::vector<gr_complex> samples_interf(window.win_len);

    if (is_kind_upchirp(window.Tu)) { // normal case
      volk_32fc_x2_multiply_32fc(&samples_interf[0], &in[0],
                                 &m_ref_downchirp[0], window.win_len);

      for (uint n = 0; n < window.win_len; n++) {
        double ph = ((double)Su) * ((double)n) / m_N;
        samples_interf[n] =
            samples_interf[n] -
            std::sqrt(Pu) * gr_expj(theta_u + (2.0 * M_PI * ph));
      }
    } else if (is_kind_downchirp(window.Tu)) { // removing downchirps

      for (uint n = 0; n < window.win_len; n++) {
        double ph = ((double)Su) * ((double)n) / m_N;
        samples_interf[n] = in[n] - std::sqrt(Pu) * m_ref_downchirp[n] *
                                        gr_expj(theta_u + (2.0 * M_PI * ph));
      }

      volk_32fc_x2_multiply_32fc(&samples_interf[0], &samples_interf[0],
                                 &m_ref_downchirp[0], window.win_len);
    } else { // nothing to remove, occurs at re-synchronization only dechirping
             // is required
      volk_32fc_x2_multiply_32fc(&samples_interf[0], &in[0],
                                 &m_ref_downchirp[m_N - window.win_len],
                                 window.win_len);
    }

    double max_l1 = 0;
    if (is_kind_upchirp(window.Ti1)) {
      for (int i = 0; i < m_N; i++) {
        Mi1[i] = matched_filter1(&samples_interf[0], window.win_len, i,
                                 window.tau, window.delta_cfo, window.Tu);

        // std::cout << "Si1=" << i << ", L=" << l1 << std::endl;
        if (std::abs(Mi1[i]) > max_l1) {
          Si1 = i;
          max_l1 = std::abs(Mi1[i]);
        }
      }
    }

    double max_l2 = 0;
    if ((is_kind_upchirp(window.Ti2))) {

      for (int i = 0; i < m_N; i++) {

        Mi2[i] = matched_filter2(&samples_interf[0], window.win_len, i,
                                 window.tau, window.delta_cfo, window.Tu);

        if (std::abs(Mi2[i]) > max_l2) {
          Si2 = i;
          max_l2 = std::abs(Mi2[i]);
        }
      }
    }

    double Li1 = boost::math::cyl_bessel_i(0, std::sqrt(Pi) * max_l1 / Pu);
    if (max_l2 > 10E10) { // TODO might be useless now
      std::cerr << RED << "[partial_ml.cc] ERROR: invalid Mi2 output value!"
                << RESET << std::endl;
      max_l2 = 0;
    }

    double Li2 = boost::math::cyl_bessel_i(0, std::sqrt(Pi) * max_l2 / Pu);
    double L = Lu * Li1 * Li2;

    consume_each(window.win_len);

    add_demod_tag(Su, Si1, Si2, Mu, max_l1, max_l2, SNR_est);

    out_L[0] = L;
    memcpy(&out_Mi1[0], &Mi1[0], sizeof(gr_complex) * m_N);
    memcpy(&out_Mi2[0], &Mi2[0], sizeof(gr_complex) * m_N);

    return 1;
  }
  std::cerr << RED << " partial_ml " << m_id << " has no output space!"
            << std::endl;
  return 0;
}

} /* namespace lora_sdr */
} /* namespace gr */
