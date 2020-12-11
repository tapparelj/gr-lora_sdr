#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Sim Lor
# Description: Simulation example LoRa
# GNU Radio version: 3.8.1.0

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
import threading


class sim_lor(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Sim Lor")

        self._lock = threading.RLock()

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
        self.cr = cr = 3

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=4,
                decimation=1,
                taps=None,
                fractional_bw=None)
        self.lora_sdr_hier_tx_0 = lora_sdr.hier_tx(pay_len, n_frame, '', cr, sf, impl_head,has_crc, samp_rate, bw)
        self.lora_sdr_hier_rx_0 = lora_sdr.hier_rx(samp_rate, bw, sf, impl_head, cr, pay_len, has_crc)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_random_0_1_0, 'strobe'), (self.lora_sdr_hier_tx_0, 'trigg'))
        self.connect((self.blocks_throttle_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.lora_sdr_hier_tx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.lora_sdr_hier_rx_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        with self._lock:
            self.bw = bw
            self.set_samp_rate(self.bw)

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        with self._lock:
            self.sf = sf

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        with self._lock:
            self.samp_rate = samp_rate
            self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        with self._lock:
            self.pay_len = pay_len

    def get_n_frame(self):
        return self.n_frame

    def set_n_frame(self, n_frame):
        with self._lock:
            self.n_frame = n_frame

    def get_mult_const(self):
        return self.mult_const

    def set_mult_const(self, mult_const):
        with self._lock:
            self.mult_const = mult_const

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        with self._lock:
            self.impl_head = impl_head

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        with self._lock:
            self.has_crc = has_crc

    def get_frame_period(self):
        return self.frame_period

    def set_frame_period(self, frame_period):
        with self._lock:
            self.frame_period = frame_period
            self.blocks_message_strobe_random_0_1_0.set_mean(self.frame_period)

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        with self._lock:
            self.cr = cr





def main(top_block_cls=sim_lor, options=None):
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
