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

#include "noise_est_impl.h"
#include <gnuradio/io_signature.h>
#include <numeric>

namespace gr {
namespace lora_sdr {

noise_est::sptr noise_est::make(uint32_t n_samples) {
  return gnuradio::get_initial_sptr(new noise_est_impl(n_samples));
}

/**
 * @brief Construct a new noise est impl::noise est impl object
 *
 * @param n_samples
 */
noise_est_impl::noise_est_impl(uint32_t n_samples)
    : gr::sync_block("noise_est",
                     gr::io_signature::make(1, 1, sizeof(gr_complex)),
                     gr::io_signature::make(0, 0, 0)) {
  m_n_samples = n_samples;
  is_first = true;

  message_port_register_out(pmt::mp("noise_est"));
}

/**
 * @brief Destroy the noise est impl::noise est impl object
 *
 */
noise_est_impl::~noise_est_impl() {}

/**
 * @brief 
 * 
 * @param noutput_items 
 * @param input_items 
 * @param output_items 
 * @return int 
 */
int noise_est_impl::work(int noutput_items,
                         gr_vector_const_void_star &input_items,
                         gr_vector_void_star &output_items) {
  const gr_complex *in = (const gr_complex *)input_items[0];

  if (noutput_items >= m_n_samples &&
      is_first) { // Noise estimation performed once on the flowgraph start.
    is_first = false;
    // estimate noise
    std::vector<float> mag_sq(m_n_samples, 0);
    volk_32fc_magnitude_squared_32f(&mag_sq[0], &in[0], m_n_samples);

    float avg_mag_sq =
        std::accumulate(mag_sq.begin(), mag_sq.end(), 0.0) / m_n_samples;

    gr_complex avg = 0;

    for (size_t i = 0; i < m_n_samples; i++) {
      avg += in[i];
    }
    avg /= m_n_samples;

    m_noise_est = avg_mag_sq - std::abs(avg) * std::abs(avg);
    message_port_pub(pmt::intern("noise_est"), pmt::from_double(m_noise_est));
    return noutput_items;
  } else if (is_first) {
    return 0;
  } else {
    return noutput_items;
  }
}

} /* namespace lora_sdr */
} /* namespace gr */
