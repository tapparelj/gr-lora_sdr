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

#ifndef INCLUDED_LORA_SDR_NOISE_EST_IMPL_H
#define INCLUDED_LORA_SDR_NOISE_EST_IMPL_H

#include <lora_sdr/noise_est.h>
#include <volk/volk.h>

namespace gr {
namespace lora_sdr {
class noise_est_impl : public noise_est {
private:
  /**
   * @brief Number of samples used for the noise estimation
   * 
   */
  uint32_t m_n_samples; 
  
  /**
   * @brief  Noise estimation
   * 
   */
  float m_noise_est;
  
  /**
   * @brief Indicate that the noise estimation has not been performed yet
   * 
   */
  bool is_first; 

public:
  /**
   * @brief Construct a new noise est impl object
   *
   * @param n_samples
   */
  noise_est_impl(uint32_t n_samples);
  /**
   * @brief Destroy the noise est impl object
   *
   */
  ~noise_est_impl();

  /**
   * @brief 
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

#endif /* INCLUDED_LORA_SDR_NOISE_EST_IMPL_H */
