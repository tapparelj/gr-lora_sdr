/* -*- c++ -*- */
/*
 * Copyright 2020 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_LORA_SDR_FRAME_SRC_H
#define INCLUDED_LORA_SDR_FRAME_SRC_H

#include <lora_sdr/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API frame_src : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<frame_src> sptr;

      /*!
       * \brief Produce frames at a regular interval
       * 
       * Output frames are composed of 8 upchirps, 2 sync words (8 and 16), 2.25 downchirps and 'pay_len' symbols.
       * The first frame is output after 'offset' samples and each frame after is spaced of 'delay' samples. If rand_sto is true, the sto will vary 
       * for each frame, with a value uniformly distributed in [0, os_factor*2^sf). Zeros are output between frames. If a file_sink is connected, the payload
       * will be random for each frame and saved to the file selected. Else a fix payload defined in frame_src_impl.cc will be used.
       *
       * \param sf Spreading factor
       * \param pay_len length of the payload in number of symbols 
       * \param delay number of samples between two frames
       * \param offset number of samples before the first frame (used to emulate the sampling frequency offset).! The offset of the first user should be smaller than 2^'sf'*'os_factor'!
       * \param cfo Carrier frequency offset
       * \param n_frames Number of frames to send
       * \param os_factor Oversampling factor
       * \param rand_sto Indicate to use a random sto for each frame
       */
      static sptr make(uint8_t sf,  int pay_len, int delay, int offset, float cfo, int n_frames, int os_factor, bool rand_sto);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_SRC_H */
