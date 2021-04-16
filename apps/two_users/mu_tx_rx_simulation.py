#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Mu Tx Rx Simulation
# Description: example of a configuration that send and receives frames for BER measurement (here the two USRPs are linked by a MIMO cable)
# GNU Radio version: 3.8.2.0

from gnuradio import blocks
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import lora_sdr
import numpy as np
import time,cmath


class mu_tx_rx_simulation(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Mu Tx Rx Simulation")

        ##################################################
        # Variables
        ##################################################
        self.bw = bw = 250e3
        self.sto = sto = [0.0,32.0]
        self.snr_thres = snr_thres = -9
        self.sf = sf = 7
        self.samp_rate = samp_rate = bw
        self.rand_sto = rand_sto = [False,False]
        self.power = power = [0,3]
        self.pay_len = pay_len = 32
        self.os_factor = os_factor = 8
        self.n_frame = n_frame = 10
        self.measurement_folder = measurement_folder = "/home/jtappare/Documents/lora_gnu_radio_prototype/gr-lora_sdr/matlab/measurements"
        self.delay = delay = 400
        self.cfo = cfo = [0.0,0.0]
        self.center_freq = center_freq = 868e6
        self.TX_gain = TX_gain = 10
        self.RX_gain = RX_gain = 10

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_signal_detector_0 = lora_sdr.signal_detector(sf, os_factor, 10, 8, 4, 50)
        self.lora_sdr_signal_detector_0.set_min_output_buffer(10240)
        self.lora_sdr_noise_est_0 = lora_sdr.noise_est(2**sf*30)
        self.lora_sdr_mu_synchro_0 = lora_sdr.mu_synchro(sf, os_factor, pay_len)
        self.lora_sdr_mu_synchro_0.set_min_output_buffer(25600)
        self.lora_sdr_mu_detection_0 = lora_sdr.mu_detection(sf, os_factor, snr_thres)
        self.lora_sdr_mu_detection_0.set_min_output_buffer(1024)
        self.lora_sdr_mu_demod_0 = lora_sdr.mu_demod(sf, 5)
        self.lora_sdr_mu_demod_0.set_min_output_buffer(25600)
        self.lora_sdr_frame_src_0_0 = lora_sdr.frame_src(sf, pay_len, int(delay*os_factor*2**sf), int(np.round((15*2**sf+sto[1])*os_factor)), cfo[1], n_frame, os_factor, rand_sto[1])
        self.lora_sdr_frame_src_0 = lora_sdr.frame_src(sf, pay_len, int(delay*os_factor*2**sf), int(np.round(sto[0]*os_factor)), cfo[0], n_frame, os_factor, rand_sto[0])
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=np.sqrt(0),
            frequency_offset=0.0,
            epsilon=1.0,
            taps=[(1.0/0.9 + 0.0j)*cmath.exp(1j*0)],
            noise_seed=0,
            block_tags=False)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate*os_factor,True)
        self.blocks_throttle_0.set_min_output_buffer(20480)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_cc(10**((power[1])/20.0))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**((power[0])/20.0))
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, os_factor)
        self.blocks_keep_one_in_n_0.set_min_output_buffer(30720)
        self.blocks_file_sink_3_0 = blocks.file_sink(gr.sizeof_short*1, measurement_folder + "/mu_source_s2.txt", False)
        self.blocks_file_sink_3_0.set_unbuffered(False)
        self.blocks_file_sink_3 = blocks.file_sink(gr.sizeof_short*1, measurement_folder + "/mu_source_s1.txt", False)
        self.blocks_file_sink_3.set_unbuffered(False)
        self.blocks_file_sink_1_0_1 = blocks.file_sink(gr.sizeof_int*1, measurement_folder + "/sync_state.txt", False)
        self.blocks_file_sink_1_0_1.set_unbuffered(False)
        self.blocks_file_sink_1_0_0 = blocks.file_sink(gr.sizeof_float*1, measurement_folder + "/mu_snr.txt", False)
        self.blocks_file_sink_1_0_0.set_unbuffered(False)
        self.blocks_file_sink_1_0 = blocks.file_sink(gr.sizeof_short*1, measurement_folder + "/mu_demod_s2.txt", False)
        self.blocks_file_sink_1_0.set_unbuffered(False)
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_short*1, measurement_folder + "/mu_demod_s1.txt", False)
        self.blocks_file_sink_1.set_unbuffered(False)
        self.blocks_delay_0_0_2 = blocks.delay(gr.sizeof_gr_complex*1, int(2**sf*os_factor*150))
        self.blocks_delay_0_0_1 = blocks.delay(gr.sizeof_gr_complex*1, 2**sf*os_factor*150)
        self.blocks_add_xx_0 = blocks.add_vcc(1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_noise_est_0, 'noise_est'), (self.lora_sdr_mu_detection_0, 'noise_est'))
        self.connect((self.blocks_add_xx_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_delay_0_0_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_delay_0_0_2, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.lora_sdr_noise_est_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_delay_0_0_2, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_delay_0_0_1, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.lora_sdr_signal_detector_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.lora_sdr_frame_src_0, 1), (self.blocks_file_sink_3, 0))
        self.connect((self.lora_sdr_frame_src_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.lora_sdr_frame_src_0_0, 1), (self.blocks_file_sink_3_0, 0))
        self.connect((self.lora_sdr_frame_src_0_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.lora_sdr_mu_demod_0, 0), (self.blocks_file_sink_1, 0))
        self.connect((self.lora_sdr_mu_demod_0, 1), (self.blocks_file_sink_1_0, 0))
        self.connect((self.lora_sdr_mu_demod_0, 2), (self.blocks_file_sink_1_0_0, 0))
        self.connect((self.lora_sdr_mu_detection_0, 0), (self.lora_sdr_mu_synchro_0, 0))
        self.connect((self.lora_sdr_mu_synchro_0, 1), (self.blocks_file_sink_1_0_1, 0))
        self.connect((self.lora_sdr_mu_synchro_0, 0), (self.lora_sdr_mu_demod_0, 0))
        self.connect((self.lora_sdr_signal_detector_0, 0), (self.lora_sdr_mu_detection_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_samp_rate(self.bw)

    def get_sto(self):
        return self.sto

    def set_sto(self, sto):
        self.sto = sto

    def get_snr_thres(self):
        return self.snr_thres

    def set_snr_thres(self, snr_thres):
        self.snr_thres = snr_thres

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.blocks_delay_0_0_1.set_dly(2**self.sf*self.os_factor*150)
        self.blocks_delay_0_0_2.set_dly(int(2**self.sf*self.os_factor*150))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate*self.os_factor)

    def get_rand_sto(self):
        return self.rand_sto

    def set_rand_sto(self, rand_sto):
        self.rand_sto = rand_sto

    def get_power(self):
        return self.power

    def set_power(self, power):
        self.power = power
        self.blocks_multiply_const_vxx_0.set_k(10**((self.power[0])/20.0))
        self.blocks_multiply_const_vxx_0_1.set_k(10**((self.power[1])/20.0))

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_os_factor(self):
        return self.os_factor

    def set_os_factor(self, os_factor):
        self.os_factor = os_factor
        self.blocks_delay_0_0_1.set_dly(2**self.sf*self.os_factor*150)
        self.blocks_delay_0_0_2.set_dly(int(2**self.sf*self.os_factor*150))
        self.blocks_keep_one_in_n_0.set_n(self.os_factor)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate*self.os_factor)

    def get_n_frame(self):
        return self.n_frame

    def set_n_frame(self, n_frame):
        self.n_frame = n_frame

    def get_measurement_folder(self):
        return self.measurement_folder

    def set_measurement_folder(self, measurement_folder):
        self.measurement_folder = measurement_folder
        self.blocks_file_sink_1.open(self.measurement_folder + "/mu_demod_s1.txt")
        self.blocks_file_sink_1_0.open(self.measurement_folder + "/mu_demod_s2.txt")
        self.blocks_file_sink_1_0_0.open(self.measurement_folder + "/mu_snr.txt")
        self.blocks_file_sink_1_0_1.open(self.measurement_folder + "/sync_state.txt")
        self.blocks_file_sink_3.open(self.measurement_folder + "/mu_source_s1.txt")
        self.blocks_file_sink_3_0.open(self.measurement_folder + "/mu_source_s2.txt")

    def get_delay(self):
        return self.delay

    def set_delay(self, delay):
        self.delay = delay

    def get_cfo(self):
        return self.cfo

    def set_cfo(self, cfo):
        self.cfo = cfo

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq

    def get_TX_gain(self):
        return self.TX_gain

    def set_TX_gain(self, TX_gain):
        self.TX_gain = TX_gain

    def get_RX_gain(self):
        return self.RX_gain

    def set_RX_gain(self, RX_gain):
        self.RX_gain = RX_gain





def main(top_block_cls=mu_tx_rx_simulation, options=None):
    tb = top_block_cls()

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
