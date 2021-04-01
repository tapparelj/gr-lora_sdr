#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Debug Mu Tx Rx
# Description: example of a configuration that send and receives frames for BER measurement (here the two USRPs are linked by a MIMO cable)
# Generated: Mon Nov 30 16:02:55 2020
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import lora_sdr
import numpy as np
import time
import wx


class debug_mu_tx_rx(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Debug Mu Tx Rx")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.sf = sf = 7
        self.os_factor_tx = os_factor_tx = 8
        self.digital_gain = digital_gain = -20
        self.bw = bw = 250e3
        self.sto = sto = [0.0,0.0]
        self.snr_thres = snr_thres = -9
        self.samp_rate = samp_rate = bw
        self.rand_sto = rand_sto = [False,False]
        self.power = power = [-np.inf,digital_gain]
        self.pay_len = pay_len = 120
        self.os_factor_rx = os_factor_rx = 8
        self.n_frame = n_frame = 100000
        self.delay = delay = int(0*os_factor_tx*2**sf)
        self.cfo = cfo = [0.0,0.0]
        self.center_freq = center_freq = 868e6
        self.calib_off_u2 = calib_off_u2 = 0.4
        self.TX_gain = TX_gain = 10
        self.RX_gain = RX_gain = 10

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("addr0=192.168.10.3,addr1=192.168.10.2", '')),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(2),
        	),
        )
        self.uhd_usrp_sink_0.set_clock_source('mimo', 1)
        self.uhd_usrp_sink_0.set_time_source('mimo', 1)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate*os_factor_tx)
        self.uhd_usrp_sink_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_sink_0.set_gain(TX_gain, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_bandwidth(bw, 0)
        self.uhd_usrp_sink_0.set_center_freq(center_freq, 1)
        self.uhd_usrp_sink_0.set_gain(TX_gain, 1)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 1)
        self.uhd_usrp_sink_0.set_bandwidth(bw, 1)
        self.lora_sdr_frame_src_0_0 = lora_sdr.frame_src(sf, bw, pay_len, delay, int(np.round((15*2**sf+sto[1])*os_factor_tx)), cfo[1], n_frame, os_factor_tx, rand_sto[1])
        self.lora_sdr_frame_src_0 = lora_sdr.frame_src(sf, bw, pay_len, delay, int(np.round(sto[0]*os_factor_tx)), cfo[0], n_frame, os_factor_tx, rand_sto[0])
        _digital_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._digital_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_digital_gain_sizer,
        	value=self.digital_gain,
        	callback=self.set_digital_gain,
        	label='digital_gain',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._digital_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_digital_gain_sizer,
        	value=self.digital_gain,
        	callback=self.set_digital_gain,
        	minimum=-20,
        	maximum=3,
        	num_steps=23,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_digital_gain_sizer)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_vcc((10**((power[1]+calib_off_u2)/20.0), ))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((10**((power[0])/20.0), ))
        self.blocks_delay_0_0_2 = blocks.delay(gr.sizeof_gr_complex*1, int(2**sf*os_factor_tx*150))
        self.blocks_delay_0_0_1 = blocks.delay(gr.sizeof_gr_complex*1, 2**sf*os_factor_tx*150)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate*os_factor_tx, analog.GR_SIN_WAVE, 0*samp_rate/2**sf, 10**(-4.2/20.0), 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.blocks_delay_0_0_1, 0), (self.uhd_usrp_sink_0, 1))
        self.connect((self.blocks_delay_0_0_2, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_delay_0_0_1, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_delay_0_0_2, 0))
        self.connect((self.lora_sdr_frame_src_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.lora_sdr_frame_src_0_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.set_delay(int(0*self.os_factor_tx*2**self.sf))
        self.blocks_delay_0_0_2.set_dly(int(2**self.sf*self.os_factor_tx*150))
        self.blocks_delay_0_0_1.set_dly(2**self.sf*self.os_factor_tx*150)
        self.analog_sig_source_x_0.set_frequency(0*self.samp_rate/2**self.sf)

    def get_os_factor_tx(self):
        return self.os_factor_tx

    def set_os_factor_tx(self, os_factor_tx):
        self.os_factor_tx = os_factor_tx
        self.set_delay(int(0*self.os_factor_tx*2**self.sf))
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate*self.os_factor_tx)
        self.blocks_delay_0_0_2.set_dly(int(2**self.sf*self.os_factor_tx*150))
        self.blocks_delay_0_0_1.set_dly(2**self.sf*self.os_factor_tx*150)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate*self.os_factor_tx)

    def get_digital_gain(self):
        return self.digital_gain

    def set_digital_gain(self, digital_gain):
        self.digital_gain = digital_gain
        self.set_power([-np.inf,self.digital_gain])
        self._digital_gain_slider.set_value(self.digital_gain)
        self._digital_gain_text_box.set_value(self.digital_gain)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_samp_rate(self.bw)
        self.uhd_usrp_sink_0.set_bandwidth(self.bw, 0)
        self.uhd_usrp_sink_0.set_bandwidth(self.bw, 1)

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
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate*self.os_factor_tx)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate*self.os_factor_tx)
        self.analog_sig_source_x_0.set_frequency(0*self.samp_rate/2**self.sf)

    def get_rand_sto(self):
        return self.rand_sto

    def set_rand_sto(self, rand_sto):
        self.rand_sto = rand_sto

    def get_power(self):
        return self.power

    def set_power(self, power):
        self.power = power
        self.blocks_multiply_const_vxx_0_1.set_k((10**((self.power[1]+self.calib_off_u2)/20.0), ))
        self.blocks_multiply_const_vxx_0.set_k((10**((self.power[0])/20.0), ))

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_os_factor_rx(self):
        return self.os_factor_rx

    def set_os_factor_rx(self, os_factor_rx):
        self.os_factor_rx = os_factor_rx

    def get_n_frame(self):
        return self.n_frame

    def set_n_frame(self, n_frame):
        self.n_frame = n_frame

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

    def get_calib_off_u2(self):
        return self.calib_off_u2

    def set_calib_off_u2(self, calib_off_u2):
        self.calib_off_u2 = calib_off_u2
        self.blocks_multiply_const_vxx_0_1.set_k((10**((self.power[1]+self.calib_off_u2)/20.0), ))

    def get_TX_gain(self):
        return self.TX_gain

    def set_TX_gain(self, TX_gain):
        self.TX_gain = TX_gain
        self.uhd_usrp_sink_0.set_gain(self.TX_gain, 0)

        self.uhd_usrp_sink_0.set_gain(self.TX_gain, 1)


    def get_RX_gain(self):
        return self.RX_gain

    def set_RX_gain(self, RX_gain):
        self.RX_gain = RX_gain


def main(top_block_cls=debug_mu_tx_rx, options=None):

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()
