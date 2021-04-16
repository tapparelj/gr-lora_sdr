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

#ifndef INCLUDED_LORA_SDR_FRAME_SRC_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_SRC_IMPL_H

#include <lora_sdr/frame_src.h>
#include <lora_sdr/utilities.h>
#include <volk/volk.h>

namespace gr {
namespace lora_sdr {

class frame_src_impl : public frame_src {
private:
  /**
   * @brief Transmission spreading factor
   *
   */
  uint8_t m_sf;
  /**
   * @brief Transmission sampling rate
   *
   */
  uint32_t m_samp_rate;
  /**
   * @brief Transmission bandwidth (Works only for samp_rate=bw)
   *
   */
  uint32_t m_bw;
  /**
   * @brief number of bin per loar symbol
   *
   */
  uint32_t m_N;
  /**
   * @brief oversampling factor
   *
   */
  uint8_t m_os_factor;
  /**
   * @brief number of zeros between two frames
   *
   */
  int m_delay;
  /**
   * @brief number of symbols in a frame payload
   *
   */
  int m_pay_len;
  /**
   * @brief number of frames to transmit
   *
   */
  int m_n_frames;
  /**
   * @brief the number of zeros sent before the first symbol
   *
   */
  int m_offset;
  /**
   * @brief the CFO of the user
   *
   */
  float m_cfo;
  /**
   * @brief indicate to use a random STO, uniformly distributed in
   * [0,2^sf*m_os_factor)
   *
   */
  bool m_rand_sto;

  /**
   * @brief delay between frame taking a random sto into account
   *
   */
  int m_delay_with_rand_sto;
  /**
   * @brief rand_sto val
   *
   */
  int m_sto_val;
  /**
   * @brief reference upchirp
   *
   */
  std::vector<gr_complex> m_upchirp;
  /**
   * @brief reference downchirp
   *
   */
  std::vector<gr_complex> m_downchirp;

  /**
   * @brief frame length in samples
   *
   */
  uint32_t m_frame_length;

  /**
   * @brief contains the whole frame
   *
   */
  std::vector<gr_complex> m_frame;

  /**
   * @brief variable used to wait before outputing the first frame
   *
   */
  bool is_first;

  /**
   * @brief number of upchirps in the preamble
   *
   */
  uint m_n_up;

  /**
   * @brief sample counter
   *
   */
  int m_cnt;

  /**
   * @brief frame counter
   *
   */
  uint m_frame_cnt;

  /**
   * @brief   return true if this block is responsible for the frame of the
   * first user. this decision is based on the m_offset value as for the first
   * user a value bigger than 2^sf*os_factor should not be used.
   *
   * @return true
   * @return false
   */
  bool is_first_user();

public:
  /**
   * @brief Construct a new frame src impl object
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
  frame_src_impl(uint8_t sf, int pay_len, int delay, int offset, float cfo,
                 int n_frames, int os_factor, bool rand_sto);

  /**
   * @brief Destroy the frame src impl object
   *
   */
  ~frame_src_impl();

  /**
   * @brief Standard gnuradio function
   * 
   * @param noutput_items 
   * @param input_items 
   * @param output_items 
   * @return int 
   */
  int work(int noutput_items, gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_SRC_IMPL_H */
