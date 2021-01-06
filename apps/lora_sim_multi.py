#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Simulated multi stream
# Author: Martyn van Dijke
# GNU Radio version: 3.8.2.0

from gnuradio import blocks
import pmt
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import lora_sdr


class lora_sim_multi(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Simulated multi stream")

        ##################################################
        # Variables
        ##################################################
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = bw
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 8
        self.mult_const = mult_const = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0_1 = filter.rational_resampler_ccc(
                interpolation=4,
                decimation=1,
                taps=None,
                fractional_bw=None)
        self.lora_sdr_hier_tx_0_0 = lora_sdr.hier_tx(pay_len, n_frame, 'sTomvXMuARDzMfJltZ4xSJ0dLGMDueK8PH00maiTXhiew9HzJmZzKNoP4zHkWGRC', cr, 8, impl_head,has_crc, samp_rate, bw)
        self.lora_sdr_hier_tx_0 = lora_sdr.hier_tx(pay_len, n_frame, 'DkzTEkJgm4nWmmhHddkGq6BUa7xfto3CdAlyRumnKgshlfxA73xvXnCIRRYefeZY', cr, sf, impl_head,has_crc, samp_rate, bw)
        self.lora_sdr_hier_rx_0_2_0 = lora_sdr.hier_rx(samp_rate, bw, 10, impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hier_rx_0_1_0_0_1_0 = lora_sdr.hier_rx(samp_rate, bw, 7, impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hier_rx_0_1_0_0_0_0_0 = lora_sdr.hier_rx(samp_rate, bw, 8, impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hier_rx_0_0_0_0 = lora_sdr.hier_rx(samp_rate, bw, 9, impl_head, cr, pay_len, has_crc)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern(""), 200)
        self.blocks_add_xx_0 = blocks.add_vcc(1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.lora_sdr_hier_tx_0, 'trigg'))
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.lora_sdr_hier_tx_0_0, 'trigg'))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.rational_resampler_xxx_0_1, 0))
        self.connect((self.lora_sdr_hier_tx_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.lora_sdr_hier_tx_0_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0_1, 0), (self.lora_sdr_hier_rx_0_0_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_1, 0), (self.lora_sdr_hier_rx_0_1_0_0_0_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_1, 0), (self.lora_sdr_hier_rx_0_1_0_0_1_0, 0))
        self.connect((self.rational_resampler_xxx_0_1, 0), (self.lora_sdr_hier_rx_0_2_0, 0))


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
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

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

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr





def main(top_block_cls=lora_sim_multi, options=None):
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
