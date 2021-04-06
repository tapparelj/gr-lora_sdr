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
                            bool has_crc,std::vector<uint16_t> sync_words ,bool exit) {
  return gnuradio::get_initial_sptr(new hier_rx_impl(
      samp_rate, bandwidth, sf, impl_head, cr, pay_len, has_crc, sync_words,exit));
}

/**
 * @brief Construct a new hier rx impl::hier rx impl object
 * 
 * @param samp_rate 
 * @param bandwidth 
 * @param sf 
 * @param impl_head 
 * @param cr 
 * @param pay_len 
 * @param has_crc
 * @param sync_words
 * @param exit 
 */
hier_rx_impl::hier_rx_impl(float samp_rate, uint32_t bandwidth, uint8_t sf,
                           bool impl_head, uint8_t cr, uint32_t pay_len,
                           bool has_crc, std::vector<uint16_t> sync_words, bool exit)
    : gr::hier_block2("hier_rx",
                      gr::io_signature::make(1, 1, sizeof(gr_complex)),
                      gr::io_signature::make(0, 0, 0)) {
   //Blocks definition
//   frame sync
   gr::lora_sdr::frame_sync::sptr frame_sync(
       gr::lora_sdr::frame_sync::make(samp_rate, bandwidth, sf, impl_head, sync_words));
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
   msg_connect(header_decoder, "frame_info", frame_sync, "frame_info");
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
