# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: lora_sdr_lora_rx
# Author: Tapparel Joachim  @EPFL,TCL
# GNU Radio version: 3.10.3.0

from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from . import lora_sdr_python as lora_sdr

class lora_sdr_lora_rx(gr.hier_block2):
    def __init__(self, center_freq=868100000, bw=125000, cr=1, has_crc=True, impl_head=False, pay_len=255, samp_rate=250000, sf=7,sync_word=[0x12], soft_decoding=False, ldro_mode=2, print_rx=[True,True]):
        gr.hier_block2.__init__(
            self, "lora_sdr_lora_rx",
                gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
                gr.io_signature(1, 1, gr.sizeof_char*1),
        )
        self.message_port_register_hier_out("out")


        ##################################################
        # Parameters
        ##################################################
        self.bw = bw
        self.cr = cr
        self.has_crc = has_crc
        self.impl_head = impl_head
        self.pay_len = pay_len
        self.samp_rate = samp_rate
        self.sf = sf
        self.soft_decoding = soft_decoding
        self.print_header = print_rx[0]
        self.print_payload = print_rx[1]
        self.center_freq = center_freq
        self.sync_word = sync_word


        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc,ldro_mode ,self.print_header)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping(soft_decoding)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(center_freq, bw, sf, impl_head, sync_word,int(samp_rate/bw),8)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, True)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(soft_decoding)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif( self.print_payload, False)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_crc_verif_0, 'msg'), (self, 'out'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.connect((self.lora_sdr_crc_verif_0, 0), (self, 0))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_mapping_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_mapping_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self, 0), (self.lora_sdr_frame_sync_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf

    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

