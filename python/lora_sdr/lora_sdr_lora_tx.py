# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: lora_sdr_lora_tx
# Description: Complete LoRa transmitter
# GNU Radio version: 3.10.3.0

from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from . import lora_sdr_python as lora_sdr

class lora_sdr_lora_tx(gr.hier_block2):
    def __init__(self, bw=125000, cr=1, has_crc=True, impl_head=False, samp_rate=250000, sf=7, ldro_mode=2, frame_zero_padd=2**7, ):
        gr.hier_block2.__init__(
            self, "lora_sdr_lora_tx",
                gr.io_signature(0, 0, 0),
                gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )
        self.message_port_register_hier_in("in")

        ##################################################
        # Parameters
        ##################################################
        self.bw = bw
        self.cr = cr
        self.has_crc = has_crc
        self.impl_head = impl_head
        self.samp_rate = samp_rate
        self.sf = sf
        self.frame_zero_padd = frame_zero_padd

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening(False)
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [8,16],frame_zero_padd,8)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro_mode, bw)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self, 'in'), (self.lora_sdr_whitening_0, 'msg'))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_gray_demap_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_demap_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr
        self.lora_sdr_hamming_enc_0.set_cr(self.cr)
        self.lora_sdr_header_0.set_cr(self.cr)
        self.lora_sdr_interleaver_0.set_cr(self.cr)

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.lora_sdr_gray_demap_0.set_sf(self.sf)
        self.lora_sdr_hamming_enc_0.set_sf(self.sf)
        self.lora_sdr_interleaver_0.set_sf(self.sf)
        self.lora_sdr_modulate_0.set_sf(self.sf)

