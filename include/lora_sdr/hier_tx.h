/**
 * @file hier_tx.h
 * @author your name (you@domain.com)
 * @brief
 * @version 0.1
 * @date 2021-01-05
 *
 * @copyright Copyright (c) 2021
 *
 */
#ifndef INCLUDED_LORA_SDR_HIER_TX_H
#define INCLUDED_LORA_SDR_HIER_TX_H

#include <gnuradio/hier_block2.h>
#include <lora_sdr/api.h>

namespace gr {
namespace lora_sdr {

/*!
 * \brief wrapper of Tx chain
 * (data_source, whitening, add_header,add_crc, hamming_enc, interleaver, gray
 * mapping,modulate) \ingroup lora_sdr
 *
 */
class LORA_SDR_API hier_tx : virtual public gr::hier_block2 {
public:
  typedef boost::shared_ptr<hier_tx> sptr;

  /*!
   * \brief Return a shared_ptr to a new instance of lora_sdr::hier_tx.
   *
   * To avoid accidental use of raw pointers, lora_sdr::hier_tx's
   * constructor is in a private implementation
   * class. lora_sdr::hier_tx::make is the public interface for
   * creating new instances.
   */
  static sptr make(int pay_len, int n_frames, std::string src_data, uint8_t cr,
                   uint8_t sf, bool impl_head, bool has_crc, uint32_t samp_rate,
                   uint32_t bw, uint32_t mean, bool multi_control);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_HIER_TX_H */
