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
   * @param samp_rate
   * @param bandwidth
   * @param sf
   * @param impl_head
   * @param cr
   * @param pay_len
   * @param has_crc
   * @param exit
   */
  hier_rx_impl(float samp_rate, uint32_t bandwidth, uint8_t sf, bool impl_head,
               uint8_t cr, uint32_t pay_len, bool has_crc, bool exit);
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
