#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "crc_verif_impl.h"
#include "deinterleaver_impl.h"
#include "dewhitening_impl.h"
#include "fft_demod_impl.h"
#include "frame_sync_impl.h"
#include "gray_enc_impl.h"
#include "hamming_dec_impl.h"
#include "header_decoder_impl.h"
#include "hier_rx_impl.h"
#include <gnuradio/hier_block2.h>
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

hier_rx::sptr hier_rx::make(float samp_rate, uint32_t bandwidth, uint8_t sf,
                            bool impl_head, uint8_t cr, uint32_t pay_len,
                            bool has_crc, bool exit) {
  return gnuradio::get_initial_sptr(new hier_rx_impl(
      samp_rate, bandwidth, sf, impl_head, cr, pay_len, has_crc, exit));
}

/*
 * The private constructor
 */
hier_rx_impl::hier_rx_impl(float samp_rate, uint32_t bandwidth, uint8_t sf,
                           bool impl_head, uint8_t cr, uint32_t pay_len,
                           bool has_crc, bool exit)
    : gr::hier_block2("hier_rx",
                      gr::io_signature::make(1, 1, sizeof(gr_complex)),
                      gr::io_signature::make(0, 0, 0)) {
  // Blocks definition
  // frame sync
  gr::lora_sdr::frame_sync::sptr frame_sync(
      gr::lora_sdr::frame_sync::make(samp_rate, bandwidth, sf, impl_head));
  // fft_demod
  gr::lora_sdr::fft_demod::sptr fft_demod(
      gr::lora_sdr::fft_demod::make(samp_rate, bandwidth, sf, impl_head));
  // gray encoding
  gr::lora_sdr::gray_enc::sptr gray_enc(gr::lora_sdr::gray_enc::make());
  // deinterleaver
  gr::lora_sdr::deinterleaver::sptr deinterleaver(
      gr::lora_sdr::deinterleaver::make(sf));
  // hamming decoder
  gr::lora_sdr::hamming_dec::sptr hamming_dec(
      gr::lora_sdr::hamming_dec::make());
  // header decoder
  gr::lora_sdr::header_decoder::sptr header_decoder(
      gr::lora_sdr::header_decoder::make(impl_head, cr, pay_len, has_crc));
  // dewhitening
  gr::lora_sdr::dewhitening::sptr dewhitening(
      gr::lora_sdr::dewhitening::make());
  // crc verify
  gr::lora_sdr::crc_verif::sptr crc_verify(gr::lora_sdr::crc_verif::make(exit));

  // Register output port of message
  message_port_register_hier_out(pmt::mp("msg"));
  // Connections
  // msg connections
  msg_connect(frame_sync, "new_frame", deinterleaver, "new_frame");
  msg_connect(frame_sync, "new_frame", dewhitening, "new_frame");
  msg_connect(frame_sync, "new_frame", fft_demod, "new_frame");
  msg_connect(frame_sync, "new_frame", hamming_dec, "new_frame");
  msg_connect(frame_sync, "new_frame", header_decoder, "new_frame");
  msg_connect(header_decoder, "pay_len", crc_verify, "pay_len");
  msg_connect(header_decoder, "CRC", crc_verify, "CRC");
  msg_connect(header_decoder, "CR", deinterleaver, "CR");
  msg_connect(header_decoder, "pay_len", dewhitening, "pay_len");
  msg_connect(header_decoder, "CRC", dewhitening, "CRC");
  msg_connect(header_decoder, "CR", fft_demod, "CR");
  msg_connect(header_decoder, "pay_len", frame_sync, "pay_len");
  msg_connect(header_decoder, "err", frame_sync, "err");
  msg_connect(header_decoder, "CRC", frame_sync, "crc");
  msg_connect(header_decoder, "CR", frame_sync, "CR");
  msg_connect(header_decoder, "CR", hamming_dec, "CR");
  msg_connect(crc_verify, "msg", self(), "msg");
  // normal connections
  connect(deinterleaver, 0, hamming_dec, 0);
  connect(dewhitening, 0, crc_verify, 0);
  connect(fft_demod, 0, gray_enc, 0);
  connect(frame_sync, 0, fft_demod, 0);
  connect(gray_enc, 0, deinterleaver, 0);
  connect(hamming_dec,0,header_decoder,0);
  connect(header_decoder,0,dewhitening,0);
  connect(self(),0,frame_sync,0);
}

/*
 * Our virtual destructor.
 */
hier_rx_impl::~hier_rx_impl() {}

} /* namespace lora_sdr */
} /* namespace gr */
