/**
 * @file hier_rx.h
 * @author your name (you@domain.com)
 * @brief
 * @version 0.1
 * @date 2021-01-05
 *
 * @copyright Copyright (c) 2021
 *
 */
#ifndef INCLUDED_LORA_SDR_HIER_RX_H
#define INCLUDED_LORA_SDR_HIER_RX_H

#include <gnuradio/hier_block2.h>
#include <lora_sdr/api.h>

namespace gr {
namespace lora_sdr {

/*!
 * \brief Wrapper block that hold the entire Rx chain :
(frame_sync, fft_demod, gray_decode, deinterleaver, hamming_dec, header_decoder,
dewhitening, crc_verif)
 * \ingroup lora_sdr
 *
 */
class LORA_SDR_API hier_rx : virtual public gr::hier_block2 {
public:
  typedef boost::shared_ptr<hier_rx> sptr;

  /*!
   * \brief Return a shared_ptr to a new instance of lora_sdr::hier_rx.
   *
   * To avoid accidental use of raw pointers, lora_sdr::hier_rx's
   * constructor is in a private implementation
   * class. lora_sdr::hier_rx::make is the public interface for
   * creating new instances.
   */
  static sptr make(float samp_rate, uint32_t bandwidth, uint8_t sf,
                   bool impl_head, uint8_t cr, uint32_t pay_len, bool has_crc);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_HIER_RX_H */
