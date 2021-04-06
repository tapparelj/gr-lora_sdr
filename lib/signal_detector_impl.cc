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

#include "signal_detector_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

signal_detector::sptr signal_detector::make(uint8_t sf, uint8_t os_factor,
                                            double threshold, int margin,
                                            int fft_symb, int transp_len) {
  return gnuradio::get_initial_sptr(new signal_detector_impl(
      sf, os_factor, threshold, margin, fft_symb, transp_len));
}

/**
 * @brief Construct a new signal detector impl::signal detector impl object
 *
 * @param sf
 * @param os_factor
 * @param threshold
 * @param margin
 * @param fft_symb
 * @param transp_len
 */
signal_detector_impl::signal_detector_impl(uint8_t sf, uint8_t os_factor,
                                           double threshold, int margin,
                                           int fft_symb, int transp_len)
    : gr::block("signal_detector",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {
  m_sf = sf;
  m_os_factor = os_factor;
  m_threshold = threshold;
  m_margin = margin;
  m_fft_symb = fft_symb;
  m_transp_len = transp_len;

  m_N = (uint32_t)(1u << m_sf);
  m_samples_per_symbol = m_N * m_os_factor;
  transp_duration = 0;
  first_time_tag = true;

  fft_cfg = kiss_fft_alloc(m_N * m_fft_symb, 0, NULL, NULL);
  cx_out.resize(m_N * m_fft_symb, 0.0);
  m_input_decim.resize(m_N, 0);
  m_dfts_mag.resize(m_N * m_fft_symb, 0);
  m_dechirped.resize(m_N * m_fft_symb, 0);

  m_downchirp.resize(m_N);
  for (uint n = 0; n < m_N; n++) {
    m_downchirp[n] = gr_expj(-2.0 * M_PI * (pow(n, 2) / (2 * m_N) - 0.5 * n));
  }

#ifdef GRLORA_DEBUGV
  out_file.open("../../matlab/debug/sig_detect.txt",
                std::ios::out | std::ios::trunc);
#endif
#ifdef THREAD_MEASURE
  m_init = false;
#endif
}

/**
 * @brief Destroy the signal detector impl::signal detector impl object
 * 
 */
signal_detector_impl::~signal_detector_impl() {}

void signal_detector_impl::forecast(int noutput_items,
                                    gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = m_samples_per_symbol * (m_margin + m_fft_symb);
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
int signal_detector_impl::general_work(int noutput_items,
                                       gr_vector_int &ninput_items,
                                       gr_vector_const_void_star &input_items,
                                       gr_vector_void_star &output_items) {
#ifdef THREAD_MEASURE
  if (!m_init) {
    gr::thread::thread_bind_to_processor(6);
    const pid_t tid = syscall(SYS_gettid);
    setpriority(PRIO_PROCESS, tid, 1);
    m_init = true;
  }
#endif

  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];

  float sig = 0;
  float median = 0;

  // detect overflow based on tag passed by the UHD block
  std::vector<tag_t> tags;
  get_tags_in_window(tags, 0, 0, ninput_items[0],
                     pmt::string_to_symbol("rx_time"));

  if (tags.size() > 0) {
    if (first_time_tag)
      first_time_tag = false;
    else {
      std::cout << RED
                << "[signal_detector.cc] Overflow detected: Samples "
                   "consumption too slow!"
                << RESET << std::endl;
      return WORK_DONE;
    }
  }

  // get the number of symbols we can process based on the input and output
  // buffer state
  int n_symb_to_process =
      std::min(std::floor(ninput_items[0] / m_samples_per_symbol) - m_margin -
                   m_fft_symb + 1,
               std::floor(noutput_items / m_samples_per_symbol));

  for (int n = 0; n < n_symb_to_process; n++) {
    // downsample the new symbol with a stride of m_os_factor
    for (int i = 0; i < m_N; i++) {
      m_input_decim[i] =
          in[(n + m_margin + m_fft_symb - 1) * m_samples_per_symbol +
             m_os_factor * i];
    }
    // shift left
    std::rotate(m_dechirped.begin(), m_dechirped.begin() + m_N,
                m_dechirped.end());

    // dechirp the new potential symbol
    volk_32fc_x2_multiply_32fc(&m_dechirped[(m_fft_symb - 1) * m_N],
                               &m_input_decim[0], &m_downchirp[0], m_N);

    // do the FFT
    kiss_fft(fft_cfg, (kiss_fft_cpx *)&m_dechirped[0],
             (kiss_fft_cpx *)&cx_out[0]);
    //get abs value of each fft value
    for (int i = 0; i < m_N * m_fft_symb; i++) {
      m_dfts_mag[i] = std::abs(cx_out[i]);
    }
    //get the maximum element from the fft values
    m_max_it = std::max_element(m_dfts_mag.begin(), m_dfts_mag.end());
    int argmax = std::distance(m_dfts_mag.begin(), m_max_it);

    // estimate signal
    sig = 0;
    median = 0;
    int n_bin = 3;
    //get power around peak +-1 symbol
    for (int j = -n_bin / 2; j <= n_bin / 2; j++) {
      sig += m_dfts_mag[mod(argmax + j, m_N * m_fft_symb)];
    }

    // get median value of entire fft
    std::vector<float> dft_mag(m_N * m_fft_symb);
    memcpy(&dft_mag[0], &m_dfts_mag[0], m_N * m_fft_symb * sizeof(float));
    nth_element(dft_mag.begin(), dft_mag.begin() + (m_N * m_fft_symb / 2),
                dft_mag.end());

    median = dft_mag[(m_N * m_fft_symb / 2)];

    if (sig / median > m_threshold) {

#ifdef GRLORA_DEBUGV
// std::cout <<"[signal_detector.cc] "<< "match filter enabled sig: "<<sig<<"
// median "<<median<<" "<<sig/median<<"/"<<m_threshold<< std::endl;
#endif
      transp_duration = m_samples_per_symbol * m_transp_len;
    }
  }

  consume_each(m_samples_per_symbol * n_symb_to_process);

  if (transp_duration > 0) {
    memcpy(&out[0], &in[0],
           n_symb_to_process * m_samples_per_symbol * sizeof(gr_complex));

    transp_duration -= n_symb_to_process * m_samples_per_symbol;
#ifdef GRLORA_DEBUGV
    for (size_t ii = 0; ii < n_symb_to_process; ii++) {
      out_file << sig / median << ","
               << "1," << std::endl;
    }
#endif
    // Tell runtime system how many output items we produced.
    return m_samples_per_symbol * n_symb_to_process;
  } else {
#ifdef GRLORA_DEBUGV
    for (size_t ii = 0; ii < n_symb_to_process; ii++) {
      out_file << sig / median << ","
               << "0," << std::endl;
    }
#endif
    return 0;
  }
}
} /* namespace lora_sdr */
} /* namespace gr */
