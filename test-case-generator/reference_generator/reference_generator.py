#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 "Martyn van Dijke".
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import lora_sdr
import pmt
import time
import os



class qa_tx(gr.top_block):

    # generate reference files to compare to
    def reference_generator(self):
        self.tb = gr.top_block()
        # input data into the system

        # open config file to load the settings and
        f = open("config", "r")
        file_testcase = str(f.readline()).splitlines()
        src_data = str(f.readline()).splitlines()[0]
        file_bw = int(f.readline())
        file_sf = int(f.readline())
        file_paylen = int(f.readline())
        file_impl_head = bool(f.readline())
        file_has_crc = bool(f.readline())
        file_cr = int(f.readline())
        f.close()

        ##################################################
        # Variables
        ##################################################
        self.bw = bw = file_bw
        self.sf = sf = file_sf
        self.samp_rate = samp_rate = file_bw
        self.pay_len = pay_len = file_paylen
        self.n_frame = n_frame = 2
        self.impl_head = impl_head = file_impl_head
        self.has_crc = has_crc = file_has_crc
        self.frame_period = frame_period = 200
        self.cr = cr = file_cr

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex *1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        # destination block -> complex vector sink
        dst = blocks.vector_sink_c()


        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.blocks_message_strobe_random_0_1_0, 'strobe'), (self.lora_sdr_data_source_0_1_0, 'trigg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0), (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0) ,dst)

        # self.tb.run()
        # run for 10 seconds and then close
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # #get current working folder
        base = os.getcwd()
        # #set the written data file
        file_result = base +"/reference_files/ref_" +str(file_testcase[0]) +"_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()
        return

