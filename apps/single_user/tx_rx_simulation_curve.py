#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Rx Simulation
# GNU Radio version: 3.8.2.0

from gnuradio import blocks
import pmt
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import lora_sdr
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle

payload_file='/home/jtappare/Documents/lora_gnu_radio_prototype/gr-lora_sdr/matlab/tmp_pay.bin'

class tx_rx_simulation(gr.top_block):

    def __init__(self,bw,sf,impl_head,has_crc,cr,pay_len,cfo,snr,out_file):
        gr.top_block.__init__(self, "Tx Rx Simulation")

        ##################################################
        # Variables
        ##################################################
        self.bw = bw
        self.snr = snr 
        self.sf = sf
        self.samp_rate = samp_rate = bw
        self.pay_len = pay_len
        self.impl_head = impl_head 
        self.has_crc = has_crc 
        self.cr = cr 
        self.out_file= out_file
        self.cfo = cfo
        
        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening()
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, bw, bw, [8, 16])
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_gray_decode_0 = lora_sdr.gray_decode(sf)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(bw, bw, sf, impl_head, [8, 16])
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_ccf(4, (-0.128616616593872,	-0.212206590789194,	-0.180063263231421,	3.89817183251938e-17	,0.300105438719035	,0.636619772367581	,0.900316316157106,	1	,0.900316316157106,	0.636619772367581,	0.300105438719035,	3.89817183251938e-17,	-0.180063263231421,	-0.212206590789194,	-0.128616616593872))
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
        self.interp_fir_filter_xxx_0.set_min_output_buffer(20000)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=np.sqrt(10**(-snr/10)),
            frequency_offset=cfo/2**sf,
            epsilon=1.0,
            taps=[1.0 + 0.0j],
            noise_seed=0,
            block_tags=True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate*10,True)
        self.blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, payload_file, False, 0, 0)
        self.blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, self.out_file, False)
        self.blocks_file_sink_0.set_unbuffered(False)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.connect((self.blocks_file_source_0_0, 0), (self.lora_sdr_whitening_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.interp_fir_filter_xxx_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.lora_sdr_frame_sync_0, 0))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_crc_verif_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_enc_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_decode_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_gray_enc_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_decode_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_samp_rate(self.bw)

    def get_snr(self):
        return self.snr

    def set_snr(self, snr):
        self.snr = snr
        self.channels_channel_model_0.set_noise_voltage(np.sqrt(10**(-self.snr/10)))

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.channels_channel_model_0.set_frequency_offset(self.cfo/2**self.sf)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate*10)

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

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

    def get_cfo(self):
        return self.cfo

    def set_cfo(self, cfo):
        self.cfo = cfo
        self.channels_channel_model_0.set_frequency_offset(self.cfo/2**self.sf)



def main(top_block_cls=tx_rx_simulation, options=None):
    tic = time.perf_counter()
    #config
    numb_frame = 30000

    payload="01234567890123456"
    snrs = range(-14,-3,1)
    bw = 250000
    sf = 7
    impl_head = True
    has_crc = False
    cr = 4
    pay_len = len(payload)
    cfo = 0.0
    snr = 0.0
	
    out_file='/home/jtappare/Documents/lora_gnu_radio_prototype/gr-lora_sdr/matlab/rec_pay.bin'
    save_res = '/home/jtappare/Documents/lora_gnu_radio_prototype/simulation_results/PER.pickle'


    #create payload file	    
    payload_aug= (payload+",")*numb_frame

    file = open(payload_file, "wb")

    file.write(payload_aug.encode("ascii"))

    file.close()


    
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    PE=np.zeros(np.size(snrs))
    frame_rec=np.zeros(np.size(snrs))
    for idx,snr in enumerate(snrs):
        print("SNR = ",snr)
        
        tb = top_block_cls(bw,sf,impl_head,has_crc,cr,pay_len,cfo,snr,out_file)
      
        tb.set_snr(snr)
        tb.start()
        tb.wait()
 
        data = np.fromfile(out_file, dtype=np.ubyte)
        # each payload as a line
        data = np.reshape(data,(int(np.size(data)/tb.pay_len),tb.pay_len))
        
        data = data[:,2:-1]
        ref = np.fromstring(payload,np.ubyte)
        frame_rec[idx] = np.size(data,0)
        #packet errors
        PE[idx] = sum(np.sum(data!= ref[2:-1],axis=1)!=0)
        del tb
        
    
    toc = time.perf_counter()
    

    print(f"Exec time: {toc - tic:0.4f} seconds")
    with np.errstate(divide='ignore',invalid='ignore'):
        PE = np.divide (PE, frame_rec)

    pickle.dump(PE, open(save_res, "wb"))

    ax=plt.subplot(2,1,1)
    plt.subplots_adjust(hspace=0.2)
    plt.ylim([10**-4,1.1])
    plt.semilogy(snrs,PE)
    plt.title("Packet Error Rate")
    plt.grid(which='both')
    
    plt.subplot(2,1,2)
    plt.semilogy(snrs,np.divide (frame_rec,numb_frame))
    plt.title("% Packet received (over"+str(numb_frame) +")")
    plt.grid()
    plt.ylim([10**-4,1])
    pickle.dump(ax, open("../../matlab/test.pickle", "wb"))
    plt.savefig("../../matlab/test.png")
    plt.show()
    


if __name__ == '__main__':
    main()
