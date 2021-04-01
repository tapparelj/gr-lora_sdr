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

namespace gr
{
  namespace lora_sdr
  {

    class frame_src_impl : public frame_src
    {
    private:
      uint8_t m_sf;         ///< Transmission spreading factor
      uint32_t m_samp_rate; ///< Transmission sampling rate
      uint32_t m_bw;        ///< Transmission bandwidth (Works only for samp_rate=bw)
      uint32_t m_N;         ///< number of bin per loar symbol
      uint8_t m_os_factor;  ///< oversampling factor
      int m_delay;          ///< number of zeros between two frames
      int m_pay_len;        ///<number of symbols in a frame payload
      int m_n_frames;       ///< number of frames to transmit
      int m_offset;         ///<the number of zeros sent before the first symbol
      float m_cfo;          ///< the CFO of the user
      bool m_rand_sto;      ///< indicate to use a random STO, uniformly distributed in [0,2^sf*m_os_factor)

      int m_delay_with_rand_sto;           ///< delay between frame taking a random sto into account
      int m_sto_val;                       ///< rand_sto val
      std::vector<gr_complex> m_upchirp;   ///< reference upchirp
      std::vector<gr_complex> m_downchirp; ///< reference downchirp

      uint32_t m_frame_length;         ///< frame length in samples
      std::vector<gr_complex> m_frame; ///< contains the whole frame

      bool is_first; ///< variable used to wait before outputing the first frame

      uint m_n_up;      ///< number of upchirps in the preamble
      int m_cnt;        ///< sample counter
      uint m_frame_cnt; ///< frame counter

      // return true if this block is responsible for the frame of the first user.
      // this decision is based on the m_offset value as for the first user a value bigger than 2^sf*os_factor should not be used.
      bool is_first_user();

    public:
      frame_src_impl(uint8_t sf, int pay_len, int delay, int offset, float cfo, int n_frames, int os_factor, bool rand_sto);
      ~frame_src_impl();

      // Where all the action really happens
      int work(int noutput_items,
               gr_vector_const_void_star &input_items,
               gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_SRC_IMPL_H */
