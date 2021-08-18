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

#include "frame_src_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

frame_src::sptr frame_src::make(uint8_t sf, int pay_len, int delay, int offset,
                                float cfo, int n_frames, int os_factor,
                                bool rand_sto) {
  return gnuradio::get_initial_sptr(new frame_src_impl(
      sf, pay_len, delay, offset, cfo, n_frames, os_factor, rand_sto));
}

/**
 * @brief Construct a new frame src impl::frame src impl object
 *
 * @param sf
 * @param pay_len
 * @param delay
 * @param offset
 * @param cfo
 * @param n_frames
 * @param os_factor
 * @param rand_sto
 */
frame_src_impl::frame_src_impl(uint8_t sf, int pay_len, int delay, int offset,
                               float cfo, int n_frames, int os_factor,
                               bool rand_sto)
    : gr::sync_block(
          "frame_src", gr::io_signature::make(0, 0, 0),
          gr::io_signature::make2(1, 2, sizeof(gr_complex), sizeof(uint16_t))) {
  m_sf = sf;
  m_delay = delay;
  m_pay_len = pay_len;
  m_offset = offset;

  m_n_frames = n_frames;

  m_os_factor = os_factor;
  m_cfo = cfo / m_os_factor;

  m_N = (uint32_t)(1u << m_sf);

  m_rand_sto = rand_sto;
  m_delay_with_rand_sto = m_delay;

  m_downchirp.resize(m_N * m_os_factor);
  m_upchirp.resize(m_N * m_os_factor);

  build_upchirp_os_factor(&m_upchirp[0], 0, m_sf, m_os_factor);
  volk_32fc_conjugate_32fc(&m_downchirp[0], &m_upchirp[0], m_N * m_os_factor);
  // build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

  m_n_up = 8;
  m_cnt = 0;
  m_frame_cnt = 0;
  is_first = true;
  m_sto_val = 0;

  // generate the frame
  m_frame.resize((m_n_up + 4.25 + m_pay_len) * m_N * m_os_factor, 0);
  // upchirps
  for (size_t i = 0; i < m_n_up; i++) {
    memcpy(&m_frame[i * m_N * m_os_factor], &m_upchirp[0],
           m_os_factor * m_N * sizeof(gr_complex));
  }
  // sync word
  build_upchirp_os_factor(&m_frame[(m_n_up)*m_N * m_os_factor], 8, m_sf, m_os_factor);
  build_upchirp_os_factor(&m_frame[(m_n_up + 1) * m_N * m_os_factor], 16, m_sf,
                m_os_factor);

  // downchirp
  memcpy(&m_frame[(m_n_up + 2) * m_N * m_os_factor], &m_downchirp[0],
         m_os_factor * m_N * sizeof(gr_complex));
  memcpy(&m_frame[(m_n_up + 3) * m_N * m_os_factor], &m_downchirp[0],
         m_os_factor * m_N * sizeof(gr_complex));
  memcpy(&m_frame[(m_n_up + 4) * m_N * m_os_factor], &m_downchirp[0],
         m_os_factor * m_N / 4 * sizeof(gr_complex));

  // symbols used when no file sink is connected
  std::vector<int> S1{0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120};
  std::vector<int> S2{125, 115, 105, 95, 85, 75, 65, 55, 45, 35, 25, 15, 5};

  for (size_t i = 0; i < m_pay_len; i++) {
    build_upchirp_os_factor(&m_frame[(m_n_up + 4.25 + i) * m_N * m_os_factor],
                  (is_first_user() ? S1[i % S1.size()] : S2[i % S2.size()]),
                  m_sf, m_os_factor);
  }

  m_frame_length = (m_n_up + 4.25 + m_pay_len) * m_N * m_os_factor;
}

/**
 * @brief Destroy the frame src impl::frame src impl object
 * 
 */
frame_src_impl::~frame_src_impl() {}

/**
 * @brief 
 * 
 * @return true 
 * @return false 
 */
bool frame_src_impl::is_first_user() { return (m_offset < m_N * m_os_factor); }

/**
 * @brief 
 * 
 * @param noutput_items 
 * @param input_items 
 * @param output_items 
 * @return int 
 */
int frame_src_impl::work(int noutput_items,
                         gr_vector_const_void_star &input_items,
                         gr_vector_void_star &output_items) {
  gr_complex *out = (gr_complex *)output_items[0];
  uint16_t *symb_out = NULL;

  if (output_items.size() == 2)
    symb_out = (uint16_t *)output_items[1];

  for (size_t i = 0; i < noutput_items; i++) {

    if (is_first && (m_cnt == m_offset)) {
      is_first = false;
      m_cnt = 0;
    } else if (m_cnt == (m_frame_length + m_delay_with_rand_sto)) {
      if (m_rand_sto) {

        int new_sto = rand() % (m_N * m_os_factor);
        m_delay_with_rand_sto = m_delay + new_sto - m_sto_val;
        m_sto_val = new_sto;
      }

      m_cnt = 0;
      if (!(m_frame_cnt % 10) && is_first_user()) {
        std::cout << "[frame_src.cc] frame cnt: "
                  << " " << m_frame_cnt << "/" << m_n_frames << '\n';
      }
      m_frame_cnt++;
      if (m_frame_cnt >= m_n_frames) {
        return WORK_DONE;
      }
    }
    // genereate new random payload
    if (output_items.size() == 2 && m_cnt == 0 && !is_first) {
      // srand(0);
      uint16_t dec_val;
      uint16_t symb_id;
      uint32_t mask = m_N - 1;

      for (int i = 0; i < m_pay_len; i++) {
        if (i < 4) { // first symbols are the frame id
          if (!(i % 2)) {
            dec_val = (m_frame_cnt * 3) % (m_N * m_N);
            symb_id = (mask << m_sf & dec_val) >> m_sf;
          } else {
            symb_id = (mask & dec_val);
          }
          build_upchirp_os_factor(&m_frame[(m_n_up + 4.25 + i) * m_N * m_os_factor],
                        symb_id, m_sf, m_os_factor);
          symb_out[i] = symb_id;
        } else {
          dec_val = rand() % m_N;
          build_upchirp_os_factor(&m_frame[(m_n_up + 4.25 + i) * m_N * m_os_factor],
                        dec_val, m_sf, m_os_factor);
          symb_out[i] = dec_val;
        }
      }
      produce(1, m_pay_len);
    }

    else if ((is_first && m_cnt < m_offset) || m_cnt >= m_frame_length)
      out[i] = 0;
    else
      out[i] = m_frame[m_cnt] * gr_expj(2 * M_PI * m_cfo / m_N * m_cnt);
    m_cnt++;
  }
  produce(0, noutput_items);
  return WORK_CALLED_PRODUCE;
}

} /* namespace lora_sdr */
} /* namespace gr */
