#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Rx Usrp Tun
# Author: Justin Garey & Zach Naymik
# GNU Radio version: 3.10.9.2

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
from gnuradio import uhd
import time
import gnuradio.lora_sdr as lora_sdr




class tx_rx_usrp_tun(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Tx Rx Usrp Tun", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.soft_decoding = soft_decoding = True
        self.sf = sf = 7
        self.samp_rate_tx = samp_rate_tx = 250000
        self.samp_rate_rx = samp_rate_rx = 250000
        self.pay_len = pay_len = 255
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 2000
        self.cr = cr = 2
        self.center_freq = center_freq = 868.1e6
        self.bw = bw = 125000
        self.Att_dB = Att_dB = 0

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0_0 = uhd.usrp_source(
            ",".join(('', '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0_0.set_samp_rate(samp_rate_rx)
        # No synchronization enforced.

        self.uhd_usrp_source_0_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_source_0_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0_0.set_bandwidth(bw, 0)
        self.uhd_usrp_source_0_0.set_gain(20, 0)
        self.uhd_usrp_source_0_0.set_min_output_buffer((2**sf<<2))
        self.uhd_usrp_sink_0_0 = uhd.usrp_sink(
            ",".join(('', '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            'frame_len',
        )
        self.uhd_usrp_sink_0_0.set_samp_rate(samp_rate_tx)
        # No synchronization enforced.

        self.uhd_usrp_sink_0_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_sink_0_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0_0.set_bandwidth(bw, 0)
        self.uhd_usrp_sink_0_0.set_gain(10, 0)
        self.network_tuntap_pdu_0 = network.tuntap_pdu('lora-tun0', 1500, True)
        self.lora_sdr_whitening_0 = lora_sdr.whitening(True,False,',','packet_len')
        self.lora_sdr_pdu_to_whitening_msg_0 = lora_sdr.pdu_to_whitening_msg()
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate_tx, bw, [0x12], (int(20*2**sf*samp_rate_tx/bw)),8)
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, 2, 125000)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, 0, True)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(False)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( False)
        self.lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], (int(samp_rate_rx/bw)),8)
        self.lora_sdr_frame_info_to_pdu_0 = lora_sdr.frame_info_to_pdu()
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( False, False)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( False)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif( 1, False)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**((Att_dB)/20))
        self.blocks_multiply_const_vxx_0.set_min_output_buffer(10000000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_frame_info_to_pdu_0, 'pdus'), (self.network_tuntap_pdu_0, 'pdus'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.msg_connect((self.lora_sdr_pdu_to_whitening_msg_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.msg_connect((self.network_tuntap_pdu_0, 'pdus'), (self.lora_sdr_pdu_to_whitening_msg_0, 'pdus'))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.uhd_usrp_sink_0_0, 0))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_crc_verif_0, 0), (self.lora_sdr_frame_info_to_pdu_0, 0))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_mapping_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_demap_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_gray_mapping_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_demap_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.lora_sdr_frame_sync_0, 0))


    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.lora_sdr_gray_demap_0.set_sf(self.sf)
        self.lora_sdr_hamming_enc_0.set_sf(self.sf)
        self.lora_sdr_interleaver_0.set_sf(self.sf)

    def get_samp_rate_tx(self):
        return self.samp_rate_tx

    def set_samp_rate_tx(self, samp_rate_tx):
        self.samp_rate_tx = samp_rate_tx
        self.uhd_usrp_sink_0_0.set_samp_rate(self.samp_rate_tx)

    def get_samp_rate_rx(self):
        return self.samp_rate_rx

    def set_samp_rate_rx(self, samp_rate_rx):
        self.samp_rate_rx = samp_rate_rx
        self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate_rx)

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc

    def get_frame_period(self):
        return self.frame_period

    def set_frame_period(self, frame_period):
        self.frame_period = frame_period

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr
        self.lora_sdr_hamming_enc_0.set_cr(self.cr)
        self.lora_sdr_header_0.set_cr(self.cr)
        self.lora_sdr_interleaver_0.set_cr(self.cr)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_sink_0_0.set_center_freq(self.center_freq, 0)
        self.uhd_usrp_source_0_0.set_center_freq(self.center_freq, 0)
        self.uhd_usrp_source_0_0.set_center_freq(self.center_freq, 1)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.uhd_usrp_sink_0_0.set_bandwidth(self.bw, 0)
        self.uhd_usrp_source_0_0.set_bandwidth(self.bw, 0)
        self.uhd_usrp_source_0_0.set_bandwidth(self.bw, 1)

    def get_Att_dB(self):
        return self.Att_dB

    def set_Att_dB(self, Att_dB):
        self.Att_dB = Att_dB
        self.blocks_multiply_const_vxx_0.set_k(10**((self.Att_dB)/20))




def main(top_block_cls=tx_rx_usrp_tun, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
