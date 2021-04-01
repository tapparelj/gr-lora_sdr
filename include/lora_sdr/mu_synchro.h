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


#ifndef INCLUDED_LORA_SDR_MU_SYNCHRO_H
#define INCLUDED_LORA_SDR_MU_SYNCHRO_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API mu_synchro : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<mu_synchro> sptr;

      /*!
       * \brief Synchronise to the strongest user present
       *
       * This block main purpose is to always output samples that are synchronised to the strongest user present. It applies the STO and CFO correction required, 
       * based on the estimation provided by the user detection stage. It outputs windows of samples that can be used by the demodulation stage to correctly interpet
       * the user configuration. Each window start with a tag specifying the power of each user, the size of the window, the type of symbol present in the windows for each user (VOID, UPCHIRP, SYNC_WORD, DOWNCHIRP, QUARTER_DOWN, PAYLOAD or UNDETERMINED),
       * the offset between the beginning of the window and the new symbol of the non-synchronised user and the CFO between the two users.
       * 
       * \param sf Spreading factor
       * \param os_factor Oversampling factor
       * \param len Number of symbols in payload
       */
      static sptr make(uint8_t sf, uint8_t os_factor, uint32_t len);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_MU_SYNCHRO_H */

