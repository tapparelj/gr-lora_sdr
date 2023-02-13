#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Rx Functionnality Check
# Author: Tapparel Joachim@EPFL,TCL
# GNU Radio version: 3.10.3.0

from gnuradio import blocks
import pmt
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gnuradio.lora_sdr as lora_sdr




class tx_rx_functionnality_check(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Tx Rx Functionnality Check", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.bw = bw = 125000
        self.sync_word = sync_word = 0x12
        self.soft_decoding = soft_decoding = False
        self.sf = sf = 7
        self.samp_rate = samp_rate = bw*4
        self.preamb_len = preamb_len = 8
        self.pay_len = pay_len = 255
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.cr = cr = 0
        self.clk_offset = clk_offset = 0
        self.center_freq = center_freq = 868.1e6
        self.SNRdB = SNRdB = -5

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening(False,",")
        self.lora_sdr_payload_id_inc_0 = lora_sdr.payload_id_inc(':')
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, int(samp_rate), bw, [sync_word], (int(20*2**sf*samp_rate/bw)),preamb_len)
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, 2, bw)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, 2, True)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        self.lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [sync_word], (int(samp_rate/bw)),preamb_len)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, True)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif( True, False)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=(10**(-SNRdB/20)),
            frequency_offset=(center_freq*clk_offset*1e-6/samp_rate),
            epsilon=(1.0+clk_offset*1e-6),
            taps=[1.0 + 0.0j],
            noise_seed=0,
            block_tags=True)
        self.channels_channel_model_0.set_min_output_buffer((int((2**sf+2)*samp_rate/bw)))
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, (samp_rate*10),True)
        self.blocks_message_strobe_0_0 = blocks.message_strobe(pmt.intern("Hello world: 0"), 2000)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, (int(2**sf*samp_rate/bw*10.1)))


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0_0, 'strobe'), (self.lora_sdr_payload_id_inc_0, 'msg_in'))
        self.msg_connect((self.blocks_message_strobe_0_0, 'strobe'), (self.lora_sdr_whitening_0, 'msg'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.msg_connect((self.lora_sdr_payload_id_inc_0, 'msg_out'), (self.blocks_message_strobe_0_0, 'set_msg'))
        self.connect((self.blocks_delay_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.lora_sdr_frame_sync_0, 0))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
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
        self.connect((self.lora_sdr_modulate_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_samp_rate(self.bw*4)
        self.blocks_delay_0.set_dly((int(2**self.sf*self.samp_rate/self.bw*10.1)))

    def get_sync_word(self):
        return self.sync_word

    def set_sync_word(self, sync_word):
        self.sync_word = sync_word

    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.blocks_delay_0.set_dly((int(2**self.sf*self.samp_rate/self.bw*10.1)))
        self.lora_sdr_gray_demap_0.set_sf(self.sf)
        self.lora_sdr_hamming_enc_0.set_sf(self.sf)
        self.lora_sdr_interleaver_0.set_sf(self.sf)
        self.lora_sdr_modulate_0.set_sf(self.sf)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_delay_0.set_dly((int(2**self.sf*self.samp_rate/self.bw*10.1)))
        self.blocks_throttle_0.set_sample_rate((self.samp_rate*10))
        self.channels_channel_model_0.set_frequency_offset((self.center_freq*self.clk_offset*1e-6/self.samp_rate))

    def get_preamb_len(self):
        return self.preamb_len

    def set_preamb_len(self, preamb_len):
        self.preamb_len = preamb_len

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

    def get_clk_offset(self):
        return self.clk_offset

    def set_clk_offset(self, clk_offset):
        self.clk_offset = clk_offset
        self.channels_channel_model_0.set_frequency_offset((self.center_freq*self.clk_offset*1e-6/self.samp_rate))
        self.channels_channel_model_0.set_timing_offset((1.0+self.clk_offset*1e-6))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.channels_channel_model_0.set_frequency_offset((self.center_freq*self.clk_offset*1e-6/self.samp_rate))

    def get_SNRdB(self):
        return self.SNRdB

    def set_SNRdB(self, SNRdB):
        self.SNRdB = SNRdB
        self.channels_channel_model_0.set_noise_voltage((10**(-self.SNRdB/20)))




def main(top_block_cls=tx_rx_functionnality_check, options=None):
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
