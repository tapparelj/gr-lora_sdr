#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Rx Simulation
# Author: Tapparel Joachim@EPFL,TCL
# GNU Radio version: 3.10.3.0

from gnuradio import blocks
import pmt
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gnuradio.lora_sdr as lora_sdr




class tx_rx_simulation(gr.top_block):

    def __init__(self,tx_payload_file, rx_payload_file, rx_crc_file, impl_head=False, soft_decoding=False, SNRdB=0, samp_rate=250000, bw=125000, center_freq=868.1, sf=7, cr=1, pay_len=32, clk_offset_ppm=0, ldro=0,preamb_len=8):
        gr.top_block.__init__(self, "Tx Rx Simulation", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.sf = sf 
        self.soft_decoding = soft_decoding 
        self.samp_rate = samp_rate 
        self.center_freq = center_freq
        self.pay_len = pay_len
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.cr = cr 
        self.bw = bw 
        self.SNRdB = SNRdB 
        self.clk_offset_ppm = clk_offset_ppm
        self.os_factor = int(samp_rate/bw)
        self.preamb_len = preamb_len 

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening(False)
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [0x12],0,preamb_len)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro,bw)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro, False)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping(soft_decoding)
        self.lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq*1e6), bw, sf, impl_head, [0x12],self.os_factor,preamb_len)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, True)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(soft_decoding)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif( False, True)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=(10**(-SNRdB/20)),
            frequency_offset = center_freq*clk_offset_ppm/samp_rate,
            epsilon=(1.0 + clk_offset_ppm*1e-6),
            taps=[1.0 + 0.0j],
            noise_seed=1,
            block_tags=True)
        self.channels_channel_model_0.set_min_output_buffer(int(2**sf*samp_rate/bw*1.1))
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, (samp_rate*10),True)
        self.blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, tx_payload_file, False, 0, 0)
        self.blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, rx_payload_file, False) 
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_char*1, rx_crc_file, False) 
        # self.probe1 = blocks.file_sink(gr.sizeof_gr_complex*1, "tmp1.bin", False) 
        # self.probe2 = blocks.file_sink(gr.sizeof_short*1, "tmp2.bin", False) 
        # self.probe2.set_unbuffered(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.connect((self.blocks_file_source_0_0, 0), (self.lora_sdr_whitening_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.lora_sdr_frame_sync_0, 0))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_crc_verif_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.lora_sdr_crc_verif_0, 1), (self.blocks_file_sink_1, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_mapping_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        # self.connect((self.lora_sdr_frame_sync_0, 0), (self.probe1, 0))
        # self.connect((self.lora_sdr_fft_demod_0, 0), (self.probe2, 0))
        self.connect((self.lora_sdr_gray_demap_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_gray_mapping_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_demap_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.set_CFO(0/2**self.sf)
        self.lora_sdr_gray_demap_0.set_sf(self.sf)
        self.lora_sdr_hamming_enc_0.set_sf(self.sf)
        self.lora_sdr_interleaver_0.set_sf(self.sf)
        self.lora_sdr_modulate_0.set_sf(self.sf)

    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate((self.samp_rate*10))

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

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr
        self.lora_sdr_hamming_enc_0.set_cr(self.cr)
        self.lora_sdr_header_0.set_cr(self.cr)
        self.lora_sdr_interleaver_0.set_cr(self.cr)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_SNRdB(self):
        return self.SNRdB

    def set_SNRdB(self, SNRdB):
        self.SNRdB = SNRdB
        self.channels_channel_model_0.set_noise_voltage((10**(-self.SNRdB/20)))

    def get_CFO(self):
        return self.CFO

    def set_CFO(self, CFO):
        self.CFO = CFO
        self.channels_channel_model_0.set_frequency_offset(self.CFO)




def main(top_block_cls=tx_rx_simulation, options=None):
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
