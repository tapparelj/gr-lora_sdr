#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: lora_sim_send
# Author: Martyn van Dijke
# GNU Radio version: 3.8.2.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import lora_sdr


class lora_sim_send(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "lora_sim_send")

        ##################################################
        # Variables
        ##################################################
        self.bw = bw = 250000
        self.time_wait = time_wait = 200
        self.threshold = threshold = 10
        self.sf = sf = 7
        self.samp_rate = samp_rate = bw
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.multi_control = multi_control = True
        self.mult_const = mult_const = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 4

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:50246', 100, False, -1)
        self.lora_sdr_hier_tx_1 = lora_sdr.hier_tx(pay_len, n_frame, "TrccpfQHyKfvXswsA4ySxtTiIvi10nSJCUJPYonkWqDHH005UmNfGuocPw3FHKc9", cr, sf, impl_head,has_crc, samp_rate, bw, time_wait, [8, 16],True)
        self.lora_sdr_hier_tx_1.set_min_output_buffer(10000000)
        self.blocks_throttle_0_1_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate*10,True)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_throttle_0_1_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.lora_sdr_hier_tx_1, 0), (self.blocks_throttle_0_1_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_samp_rate(self.bw)

    def get_time_wait(self):
        return self.time_wait

    def set_time_wait(self, time_wait):
        self.time_wait = time_wait

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0_1_0.set_sample_rate(self.samp_rate*10)

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_n_frame(self):
        return self.n_frame

    def set_n_frame(self, n_frame):
        self.n_frame = n_frame

    def get_multi_control(self):
        return self.multi_control

    def set_multi_control(self, multi_control):
        self.multi_control = multi_control

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





def main(top_block_cls=lora_sim_send, options=None):
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
