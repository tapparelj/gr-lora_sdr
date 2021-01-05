/**
 * @file hier_tx_impl.h
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2021-01-05
 * 
 * @copyright Copyright (c) 2021
 * 
 */
#ifndef INCLUDED_LORA_SDR_HIER_TX_IMPL_H
#define INCLUDED_LORA_SDR_HIER_TX_IMPL_H

#include <lora_sdr/hier_tx.h>

namespace gr {
namespace lora_sdr {

class hier_tx_impl : public hier_tx {
private:
  // Nothing to declare in this block.

public:
  /**
   * @brief Construct a new hier tx impl::hier tx impl object
   *
   * @param pay_len : payload length
   * @param n_frames : number of frames
   * @param src_data : input data, if empty generate random input data
   * @param cr : coding rate
   * @param sf : spreading factor
   * @param impl_head : impl_head mode (boolean on/off)
   * @param has_crc : has_crc mode (boolean on/off)
   * @param samp_rate : sampling rate
   * @param bw : bandwith
   * @param mean : mean time in ms
   */
  hier_tx_impl(int pay_len, int n_frames, std::string src_data, uint8_t cr,
               uint8_t sf, bool impl_head, bool has_crc, uint32_t samp_rate,
               uint32_t bw,uint32_t mean);
  ~hier_tx_impl();

  // Where all the action really happens
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_HIER_TX_IMPL_H */
