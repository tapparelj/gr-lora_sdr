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

#ifndef INCLUDED_LORA_SDR_MU_SYNCHRO_IMPL_H
#define INCLUDED_LORA_SDR_MU_SYNCHRO_IMPL_H
// #define GRLORA_DEBUG // synchronisation infos will be printed in the terminal(it is advised to transmitt only one frame)

#include <lora_sdr/mu_synchro.h>
#include <lora_sdr/utilities.h>
#include <iostream>
#include <fstream>

namespace gr
{
  namespace lora_sdr
  {

    class mu_synchro_impl : public mu_synchro
    {
    private:
      enum Sync_state
      {
        IDLE,
        SINGLE_USER,
        REALIGN_TO_NEW,
        MULTI_USER,
        REALIGN_TO_PREV

      };
      enum Detection_cases
      {
        P1_LT_P2, ///< P1 less than P2
        P1_GT_P2, ///< P1 greater than P2
        P1_OR_P2, ///< only one user detected
      };

      struct user
      {
        int32_t cnt;
        double power;
        long sto_int;
        double sto_frac;
        long cfo_int;
        double cfo_frac;
      };

      uint8_t m_sf;                  ///< Spreading factor
      uint8_t m_n_up;                ///< number of upchirps in preamble
      uint32_t m_len;                ///< number of payload symbols
      uint32_t m_samples_per_symbol; ///< Number of samples received per lora symbols
      uint32_t m_N;                  ///< 2^sf
      uint8_t m_os_factor;           ///< oversampling factor

      user user_u;
      user user_i;
      double m_power1; ///< power of user 1 (not fixed to user u)
      double m_power2; ///< power of user 2 (not fixed to user i)

      bool two_users; ///< indicate that two users are present

      double m_tau; ///< number of samples between the begin of a window and the start of the second symbol of the non synchronized user.

      uint8_t m_sync_state; ///< synchronisation state

      int m_item_to_consume; ///< number of items that should be consumed from th input buffer

      void add_tag(double power1, double power2, long win_len,
                   Symbol_type Tu, Symbol_type Ti1, Symbol_type Ti2, double tau, double delta_cfo, int offset);

      // return the symbol type given the sample counter of a user
      Symbol_type get_type(int cnt);

      // main function, responsible of the output buffer filling, window  and tag creation
      std::tuple<int, int, int> sync_frame(const gr_complex *in, gr_complex *out, uint32_t *state_out, int offset, int state_offset);

    public:
      mu_synchro_impl(uint8_t sf, uint8_t os_factor, uint32_t len);
      ~mu_synchro_impl();

      void forecast(int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_MU_SYNCHRO_IMPL_H */
