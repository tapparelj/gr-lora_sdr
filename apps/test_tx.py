#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.8.1.0

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import lora_sdr


class test_tx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")

        ##################################################
        # Variables
        ##################################################
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = bw
        self.pay_len = pay_len = 5
        self.n_frame = n_frame = 2
        self.mult_const = mult_const = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening()
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw)
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_gray_decode_0 = lora_sdr.gray_decode(sf)
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(pay_len, n_frame, 'test')
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_random_0_1_0, 'strobe'), (self.lora_sdr_data_source_0_1_0, 'trigg'))
        self.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_gray_decode_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_decode_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_samp_rate(self.bw)

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_n_frame(self):
        return self.n_frame

    def set_n_frame(self, n_frame):
        self.n_frame = n_frame

    def get_mult_const(self):
        return self.mult_const

    def set_mult_const(self, mult_const):
        self.mult_const = mult_const

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
        self.blocks_message_strobe_random_0_1_0.set_mean(self.frame_period)

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr





def main(top_block_cls=test_tx, options=None):
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
