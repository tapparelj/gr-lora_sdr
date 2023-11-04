#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Rx Simulation
# Author: Tapparel Joachim@EPFL,TCL
# GNU Radio version: 3.10.3.0
# This code generates the reference data of tx. 
# Includes all the blocks in tx_rx_simulations from file source to throtte
# Generate files into ../python/lora_sdr/qa_ref_tx

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gnuradio.lora_sdr as lora_sdr




class ref_tx_no_mod_generate(gr.top_block):

    def __init__(self, sf, cr):
        gr.top_block.__init__(self, "Tx Rx Simulation", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.soft_decoding = soft_decoding = False
        self.sf = sf 
        self.samp_rate = samp_rate = 500000
        self.preamb_len = preamb_len = 8
        self.pay_len = pay_len = 16
        self.ldro = ldro = False
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.cr = cr 
        self.clk_offset = clk_offset = 0
        self.center_freq = center_freq = 868.1e6
        self.bw = bw = 125000
        self.SNRdB = SNRdB = -5

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening = lora_sdr.whitening(False,False,',','packet_len')
        self.lora_sdr_interleaver = lora_sdr.interleaver(self.cr, self.sf, ldro, 125000)
        self.lora_sdr_header = lora_sdr.header(impl_head, has_crc, self.cr)
        self.lora_sdr_hamming_enc = lora_sdr.hamming_enc(self.cr, self.sf)
        self.lora_sdr_gray_demap = lora_sdr.gray_demap(self.sf)
        self.lora_sdr_add_crc = lora_sdr.add_crc(has_crc)
        self.blocks_file_source = blocks.file_source(gr.sizeof_char*1, "/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt", False, 0, 0)
        self.blocks_file_source.set_begin_tag(pmt.PMT_NIL)
        output_file_path = "/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx_no_mod/ref_tx_sf{}_cr{}.bin".format(self.sf, self.cr)
        self.blocks_file_sink = blocks.file_sink(gr.sizeof_int*1, output_file_path, False)
        self.blocks_file_sink.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source, 0), (self.lora_sdr_whitening, 0))
        self.connect((self.lora_sdr_gray_demap, 0), (self.blocks_file_sink, 0))
        self.connect((self.lora_sdr_add_crc, 0), (self.lora_sdr_hamming_enc, 0))
        self.connect((self.lora_sdr_hamming_enc, 0), (self.lora_sdr_interleaver, 0))
        self.connect((self.lora_sdr_header, 0), (self.lora_sdr_add_crc, 0))
        self.connect((self.lora_sdr_interleaver, 0), (self.lora_sdr_gray_demap, 0))
        self.connect((self.lora_sdr_whitening, 0), (self.lora_sdr_header, 0))


    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.lora_sdr_gray_demap.set_sf(self.sf)
        self.lora_sdr_hamming_enc.set_sf(self.sf)
        self.lora_sdr_interleaver.set_sf(self.sf)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_preamb_len(self):
        return self.preamb_len

    def set_preamb_len(self, preamb_len):
        self.preamb_len = preamb_len

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_ldro(self):
        return self.ldro

    def set_ldro(self, ldro):
        self.ldro = ldro

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
        self.lora_sdr_hamming_enc.set_cr(self.cr)
        self.lora_sdr_header.set_cr(self.cr)
        self.lora_sdr_interleaver.set_cr(self.cr)

    def get_clk_offset(self):
        return self.clk_offset

    def set_clk_offset(self, clk_offset):
        self.clk_offset = clk_offset

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_SNRdB(self):
        return self.SNRdB

    def set_SNRdB(self, SNRdB):
        self.SNRdB = SNRdB



def main(top_block_cls=ref_tx_no_mod_generate, options=None):
    # Define the range of sf and cr values
    sf_range = range(7, 12)  # sf values from 7 to 11
    cr_range = range(2, 6)   # cr values from 2 to 5

    for sf in sf_range:
        for cr in cr_range:
            # Create a new top_block instance for each combination of sf and cr
            tb = top_block_cls(sf,cr)

            # Set the sf and cr values for this iteration
            tb.set_sf(sf)
            tb.set_cr(cr)

            # Generate a unique output file path for this combination

            def sig_handler(sig=None, frame=None):
                tb.stop()
                tb.wait()

                sys.exit(0)

            signal.signal(signal.SIGINT, sig_handler)
            signal.signal(signal.SIGTERM, sig_handler)

            tb.start()
            tb.wait()

if __name__ == '__main__':
    main()

