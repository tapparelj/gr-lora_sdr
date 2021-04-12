#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Mu Tx Rx
# Description: example of a configuration that send and receives frames for BER measurement (here the two USRPs are linked by a MIMO cable)
# GNU Radio version: 3.8.2.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import lora_sdr
import numpy as np


class mu_tx_rx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Mu Tx Rx")

        ##################################################
        # Variables
        ##################################################
        self.sf = sf = 8
        self.os_factor_tx = os_factor_tx = 8
        self.bw = bw = 250e3
        self.tx_gain = tx_gain = 10
        self.sto = sto = [0.0,0.0]
        self.snr_thres = snr_thres = -9
        self.samp_rate = samp_rate = bw
        self.rx_gain = rx_gain = 10
        self.rand_sto = rand_sto = [False,False]
        self.power = power = [0,0]
        self.pay_len = pay_len = 32
        self.os_factor_rx = os_factor_rx = 8
        self.n_frame = n_frame = 5000
        self.measurement_folder = measurement_folder = "/home/jtappare/Documents/lora_gnu_radio_prototype/gr-lora_sdr/matlab/measurements"
        self.delay = delay = int(400*os_factor_tx*2**sf)
        self.cfo = cfo = [0.0,0.0]
        self.center_freq = center_freq = 868e6
        self.calib_off_u2 = calib_off_u2 = 0.4

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(('', "addr=192.168.10.4")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_bandwidth(bw*os_factor_rx, 0)
        self.uhd_usrp_source_0.set_samp_rate(bw*os_factor_rx)
        # No synchronization enforced.
        self.uhd_usrp_source_0.set_min_output_buffer(409600)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(('', "addr0=192.168.10.3,addr1=192.168.10.2")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,2)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_time_source('mimo', 1)
        self.uhd_usrp_sink_0.set_clock_source('mimo', 1)
        self.uhd_usrp_sink_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_bandwidth(bw, 0)
        self.uhd_usrp_sink_0.set_center_freq(center_freq, 1)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 1)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 1)
        self.uhd_usrp_sink_0.set_bandwidth(bw, 1)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate*os_factor_tx)
        # No synchronization enforced.
        self.lora_sdr_signal_detector_0 = lora_sdr.signal_detector(sf, os_factor_rx, 10, 8, 4, 50)
        self.lora_sdr_signal_detector_0.set_min_output_buffer(1638400)
        self.lora_sdr_noise_est_0 = lora_sdr.noise_est(2**sf*30)
        self.lora_sdr_mu_synchro_0 = lora_sdr.mu_synchro(sf, os_factor_rx, pay_len)
        self.lora_sdr_mu_synchro_0.set_min_output_buffer(51200)
        self.lora_sdr_mu_detection_0 = lora_sdr.mu_detection(sf, os_factor_rx, snr_thres)
        self.lora_sdr_mu_detection_0.set_min_output_buffer(409600)
        self.lora_sdr_mu_demod_0 = lora_sdr.mu_demod(sf, 5)
        self.lora_sdr_mu_demod_0.set_min_output_buffer(51200)
        self.lora_sdr_frame_src_0_0 = lora_sdr.frame_src(sf, pay_len, delay, int(np.round((15*2**sf+sto[1])*os_factor_tx)), cfo[1], n_frame, os_factor_tx, rand_sto[1])
        self.lora_sdr_frame_src_0 = lora_sdr.frame_src(sf, pay_len, delay, int(np.round(sto[0]*os_factor_tx)), cfo[0], n_frame, os_factor_tx, rand_sto[0])
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_cc(10**((power[1]+calib_off_u2)/20.0))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**((power[0])/20.0))
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, os_factor_rx)
        self.blocks_keep_one_in_n_0.set_min_output_buffer(61440)
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
        self.blocks_delay_0_0_2 = blocks.delay(gr.sizeof_gr_complex*1, int(2**sf*os_factor_tx*150))
        self.blocks_delay_0_0_1 = blocks.delay(gr.sizeof_gr_complex*1, 2**sf*os_factor_tx*150)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate*os_factor_tx, analog.GR_SIN_WAVE, -9.4*samp_rate/2**sf, 10**(-4.2/20.0), 0, 0)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_noise_est_0, 'noise_est'), (self.lora_sdr_mu_detection_0, 'noise_est'))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.blocks_delay_0_0_1, 0), (self.uhd_usrp_sink_0, 1))
        self.connect((self.blocks_delay_0_0_2, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.lora_sdr_noise_est_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_delay_0_0_1, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_delay_0_0_2, 0))
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
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.lora_sdr_signal_detector_0, 0))


    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.set_delay(int(400*self.os_factor_tx*2**self.sf))
        self.analog_sig_source_x_0.set_frequency(-9.4*self.samp_rate/2**self.sf)
        self.blocks_delay_0_0_1.set_dly(2**self.sf*self.os_factor_tx*150)
        self.blocks_delay_0_0_2.set_dly(int(2**self.sf*self.os_factor_tx*150))

    def get_os_factor_tx(self):
        return self.os_factor_tx

    def set_os_factor_tx(self, os_factor_tx):
        self.os_factor_tx = os_factor_tx
        self.set_delay(int(400*self.os_factor_tx*2**self.sf))
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate*self.os_factor_tx)
        self.blocks_delay_0_0_1.set_dly(2**self.sf*self.os_factor_tx*150)
        self.blocks_delay_0_0_2.set_dly(int(2**self.sf*self.os_factor_tx*150))
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate*self.os_factor_tx)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_samp_rate(self.bw)
        self.uhd_usrp_sink_0.set_bandwidth(self.bw, 0)
        self.uhd_usrp_sink_0.set_bandwidth(self.bw, 1)
        self.uhd_usrp_source_0.set_samp_rate(self.bw*self.os_factor_rx)
        self.uhd_usrp_source_0.set_bandwidth(self.bw*self.os_factor_rx, 0)
        self.uhd_usrp_source_0.set_bandwidth(self.bw, 1)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 1)

    def get_sto(self):
        return self.sto

    def set_sto(self, sto):
        self.sto = sto

    def get_snr_thres(self):
        return self.snr_thres

    def set_snr_thres(self, snr_thres):
        self.snr_thres = snr_thres

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate*self.os_factor_tx)
        self.analog_sig_source_x_0.set_frequency(-9.4*self.samp_rate/2**self.sf)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate*self.os_factor_tx)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    def get_rand_sto(self):
        return self.rand_sto

    def set_rand_sto(self, rand_sto):
        self.rand_sto = rand_sto

    def get_power(self):
        return self.power

    def set_power(self, power):
        self.power = power
        self.blocks_multiply_const_vxx_0.set_k(10**((self.power[0])/20.0))
        self.blocks_multiply_const_vxx_0_1.set_k(10**((self.power[1]+self.calib_off_u2)/20.0))

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_os_factor_rx(self):
        return self.os_factor_rx

    def set_os_factor_rx(self, os_factor_rx):
        self.os_factor_rx = os_factor_rx
        self.blocks_keep_one_in_n_0.set_n(self.os_factor_rx)
        self.uhd_usrp_source_0.set_samp_rate(self.bw*self.os_factor_rx)
        self.uhd_usrp_source_0.set_bandwidth(self.bw*self.os_factor_rx, 0)

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
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq, 0)
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq, 1)
        self.uhd_usrp_source_0.set_center_freq(self.center_freq, 0)

    def get_calib_off_u2(self):
        return self.calib_off_u2

    def set_calib_off_u2(self, calib_off_u2):
        self.calib_off_u2 = calib_off_u2
        self.blocks_multiply_const_vxx_0_1.set_k(10**((self.power[1]+self.calib_off_u2)/20.0))





def main(top_block_cls=mu_tx_rx, options=None):
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
