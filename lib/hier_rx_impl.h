/**
 * @file hier_rx_impl.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-01-15
 *
 *
 */

#ifndef INCLUDED_LORA_SDR_HIER_RX_IMPL_H
#define INCLUDED_LORA_SDR_HIER_RX_IMPL_H

#include <lora_sdr/hier_rx.h>

namespace gr {
namespace lora_sdr {

class hier_rx_impl : public hier_rx {
private:
  // Nothing to declare in this block.

public:
  /**
   * @brief Construct a new hier rx impl object
   *
   * @param samp_rate : sampling rate to use
   * @param bandwidth : bandwith to use
   * @param sf : spreading factor to use
   * @param impl_head : impl_head mode (boolean)
   * @param cr : coding rate
   * @param pay_len : payload length
   * @param has_crc : has_crc (boolean)
   * @param sync_words : syncwords to use
   * @param exit : boolean to tell system what to do on done signal (exit or not)
   */
  hier_rx_impl(float samp_rate, uint32_t bandwidth, uint8_t sf,
               bool impl_head, uint8_t cr, uint32_t pay_len,
               bool has_crc, std::vector<uint16_t> sync_words, bool exit);
  /**
   * @brief Destroy the hier rx impl object
   *
   */
  ~hier_rx_impl();

  // Where all the action really happens
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_HIER_RX_IMPL_H */
