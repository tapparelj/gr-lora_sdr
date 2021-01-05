/**
 * @file hier_tx_impl.cc
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2021-01-05
 * 
 * @copyright Copyright (c) 2021
 * 
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "hier_tx_impl.h"
#include <gnuradio/io_signature.h>
#include "add_crc_impl.h"
#include "data_source_sim_impl.h"
#include "gray_decode_impl.h"
#include "hamming_enc_impl.h"
#include "header_impl.h"
#include "hier_tx_impl.h"
#include "interleaver_impl.h"
#include "modulate_impl.h"
#include "whitening_impl.h"
#include <gnuradio/hier_block2.h>


namespace gr {
namespace lora_sdr {

hier_tx::sptr hier_tx::make(int pay_len, int n_frames, std::string src_data,
                            uint8_t cr, uint8_t sf, bool impl_head,
                            bool has_crc, uint32_t samp_rate, uint32_t bw,uint32_t mean) {
  return gnuradio::get_initial_sptr(new hier_tx_impl(pay_len, n_frames, src_data, cr, sf, impl_head, has_crc, samp_rate, bw, mean));
}


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
hier_tx_impl::hier_tx_impl(int pay_len, int n_frames, std::string src_data,
                           uint8_t cr, uint8_t sf, bool impl_head, bool has_crc,
                           uint32_t samp_rate, uint32_t bw, uint32_t mean)
    : gr::hier_block2(
          "hier_tx",
          gr::io_signature::make(0, 0, 0),
          gr::io_signature::make(1, 1, sizeof(gr_complex))) {

  // Blocks
  gr::lora_sdr::data_source_sim::sptr data_source_sim(
      gr::lora_sdr::data_source_sim::make(pay_len, n_frames, src_data,mean));
  // whitening
  gr::lora_sdr::whitening::sptr whitening(gr::lora_sdr::whitening::make());
  // add header
  gr::lora_sdr::header::sptr header(
      gr::lora_sdr::header::make(impl_head, has_crc, cr));
  // add crc
  gr::lora_sdr::add_crc::sptr add_crc(gr::lora_sdr::add_crc::make(has_crc));
  // hamming encoding
  gr::lora_sdr::hamming_enc::sptr hamming_enc(
      gr::lora_sdr::hamming_enc::make(cr, sf));
  // interleaving
  gr::lora_sdr::interleaver::sptr interleaver(
      gr::lora_sdr::interleaver::make(cr, sf));
  // gray mapping
  gr::lora_sdr::gray_decode::sptr gray_decode(
      gr::lora_sdr::gray_decode::make(sf));
  // modulate
  gr::lora_sdr::modulate::sptr modulate(
      gr::lora_sdr::modulate::make(sf, samp_rate, bw));
  gr::hier_block2::set_min_output_buffer(10000000);
  // Connections
  // Message connections
  msg_connect(data_source_sim, "msg", whitening, "msg");
  msg_connect(data_source_sim, "msg", header, "msg");
  msg_connect(data_source_sim, "msg", add_crc, "msg");
  msg_connect(data_source_sim, "msg", interleaver, "msg");
  msg_connect(data_source_sim, "msg", modulate, "msg");

  // normal connections
  connect(data_source_sim,0,whitening,0);
  connect(add_crc,0, hamming_enc,0);
  connect(gray_decode,0,modulate,0);
  connect(hamming_enc,0,interleaver,0);
  connect(interleaver,0,gray_decode,0);
  connect(modulate,0,self(),0);
}

/**
 * @brief Destroy the hier tx impl::hier tx impl object
 * 
 */
hier_tx_impl::~hier_tx_impl() {}

} /* namespace lora_sdr */
} /* namespace gr */
