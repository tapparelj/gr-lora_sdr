#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lora Tx
# GNU Radio version: 3.8.2.0

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
import soapy


class lora_TX(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Lora Tx")

        ##################################################
        # Variables
        ##################################################
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = bw
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 1000
        self.cr = cr = 4
        self.center_freq = center_freq = 868.1e6
        self.TX_gain = TX_gain = 0

        ##################################################
        # Blocks
        ##################################################
        self.soapy_sink_0 = None
        if "lime" == 'custom':
            dev = 'driver=lime_sdr'
            devname = dev.split("=", 1)[1]
        else:
            dev = 'driver=' + "lime"
            devname = "lime"

        self.soapy_sink_0 = soapy.sink(1, dev, '', samp_rate, "fc32", '')

        self.soapy_sink_0.set_gain_mode(0,False)
        self.soapy_sink_0.set_gain_mode(1,False)

        self.soapy_sink_0.set_frequency(0, center_freq)
        self.soapy_sink_0.set_frequency(1, 100.0e6)

        # Made antenna sanity check more generic
        antList = self.soapy_sink_0.listAntennas(0)

        if len(antList) > 1:
            # If we have more than 1 possible antenna
            if len('Auto') == 0 or 'Auto' not in antList:
                print("ERROR: Please define ant0 to an allowed antenna name.")
                strAntList = str(antList).lstrip('(').rstrip(')').rstrip(',')
                print("Allowed antennas: " + strAntList)
                exit(0)

            self.soapy_sink_0.set_antenna(0,'Auto')

        if 1 > 1:
            antList = self.soapy_sink_0.listAntennas(1)
            # If we have more than 1 possible antenna
            if len(antList) > 1:
                if len('TX') == 0 or 'TX' not in antList:
                    print("ERROR: Please define ant1 to an allowed antenna name.")
                    strAntList = str(antList).lstrip('(').rstrip(')').rstrip(',')
                    print("Allowed antennas: " + strAntList)
                    exit(0)

                self.soapy_sink_0.set_antenna(1,'TX')

        # Setup IQ Balance
        if devname != 'uhd' and devname != 'lime':
            if (self.soapy_sink_0.IQ_balance_support(0)):
                self.soapy_sink_0.set_iq_balance(0,0)

            if (self.soapy_sink_0.IQ_balance_support(1)):
                self.soapy_sink_0.set_iq_balance(1,0)

        # Setup Frequency correction
        if (self.soapy_sink_0.freq_correction_support(0)):
            self.soapy_sink_0.set_frequency_correction(0,0)

        if (self.soapy_sink_0.freq_correction_support(1)):
            self.soapy_sink_0.set_frequency_correction(1,0)

        if devname == 'sidekiq' or "True" == 'False':
            self.soapy_sink_0.set_gain(0,10)
            self.soapy_sink_0.set_gain(1,0)
        else:
            if devname == 'bladerf':
                 self.soapy_sink_0.set_gain(0,"txvga1", -35)
                 self.soapy_sink_0.set_gain(0,"txvga2", 0)
            elif devname == 'uhd':
                self.soapy_sink_0.set_gain(0,"PGA", 24)
                self.soapy_sink_0.set_gain(1,"PGA", 0)
            else:
                 self.soapy_sink_0.set_gain(0,"PGA", 24)
                 self.soapy_sink_0.set_gain(1,"PGA", 0)
                 self.soapy_sink_0.set_gain(0,"PAD", 20)
                 self.soapy_sink_0.set_gain(1,"PAD", 0)
                 self.soapy_sink_0.set_gain(0,"IAMP", 10)
                 self.soapy_sink_0.set_gain(1,"IAMP", 0)
                 self.soapy_sink_0.set_gain(0,"txvga1", -35)
                 self.soapy_sink_0.set_gain(0,"txvga2", 0)
                 # Only hackrf uses VGA name, so just ch0
                 self.soapy_sink_0.set_gain(0,"VGA", 10)
        self.lora_sdr_whitening_0 = lora_sdr.whitening()
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, bw, bw, [8,16])
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_gray_decode_0 = lora_sdr.gray_decode(sf)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_gr_complex*1, '', "")
        self.blocks_tag_debug_0.set_display(True)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("hello world"), frame_period)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.lora_sdr_whitening_0, 'msg'))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_gray_decode_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_decode_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.soapy_sink_0, 0))
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
        self.blocks_message_strobe_0.set_period(self.frame_period)

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.soapy_sink_0.set_frequency(0, self.center_freq)

    def get_TX_gain(self):
        return self.TX_gain

    def set_TX_gain(self, TX_gain):
        self.TX_gain = TX_gain





def main(top_block_cls=lora_TX, options=None):
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
