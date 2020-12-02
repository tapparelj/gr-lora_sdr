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
import lora_sdr_swig as lora_sdr
import pmt
import time
import filecmp
import os


class qa_tx(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_1(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/1_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_1_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_2(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/2_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_2_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_3(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/3_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_3_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_4(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/4_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_4_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_5(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/5_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_5_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_6(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/6_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_6_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_7(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/7_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_7_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_8(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/8_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_8_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_9(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/9_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_9_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_10(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/10_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_10_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_11(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/11_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_11_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_12(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/12_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_12_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_13(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/13_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_13_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_14(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/14_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_14_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_15(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/15_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_15_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_16(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/16_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_16_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_17(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/17_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_17_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_18(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/18_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_18_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_19(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/19_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_19_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_20(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/20_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_20_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_21(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/21_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_21_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_22(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/22_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_22_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_23(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/23_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_23_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_24(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/24_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_24_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_25(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/25_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_25_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_26(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/26_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_26_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_27(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/27_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_27_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_28(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/28_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_28_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_29(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/29_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_29_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_30(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/30_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_30_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_31(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/31_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_31_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_32(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/32_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_32_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_33(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/33_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_33_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_34(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/34_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_34_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_35(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/35_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_35_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_36(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/36_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_36_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_37(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/37_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_37_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_38(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/38_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_38_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_39(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/39_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_39_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_40(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 5
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/40_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_40_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_41(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/41_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_41_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_42(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/42_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_42_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_43(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/43_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_43_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_44(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/44_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_44_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_45(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/45_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_45_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_46(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/46_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_46_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_47(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/47_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_47_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_48(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 6
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/48_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_48_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_49(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/49_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_49_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_50(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/50_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_50_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_51(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/51_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_51_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_52(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/52_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_52_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_53(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/53_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_53_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_54(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/54_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_54_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_55(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/55_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_55_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_56(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/56_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_56_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_57(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/57_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_57_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_58(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/58_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_58_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_59(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/59_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_59_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_60(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/60_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_60_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_61(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/61_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_61_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_62(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/62_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_62_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_63(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/63_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_63_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')

    def test_64(self):
        ##################################################
        # Variables
        ##################################################
        # input data into the system
        src_data = "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"
        self.bw = bw = 250000
        self.sf = sf = 8
        self.samp_rate = samp_rate = 250000
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 1
        self.impl_head = impl_head = False
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 1

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
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(
            pay_len, n_frame, src_data)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex * 1)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(
            pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)
        dst = blocks.vector_sink_c()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect(
            (self.blocks_message_strobe_random_0_1_0,
             'strobe'),
            (self.lora_sdr_data_source_0_1_0,
             'trigg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect(
            (self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.connect((self.lora_sdr_add_crc_0, 0),
                        (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0),
                        (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0),
                        (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0),
                        (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_interleaver_0, 0),
                        (self.lora_sdr_gray_decode_0, 0))
        self.tb.connect((self.lora_sdr_whitening_0, 0),
                        (self.lora_sdr_header_0, 0))
        # connect to complex vector sink
        self.tb.connect((self.lora_sdr_modulate_0, 0), dst)

        # self.tb.run()
        self.tb.start()
        time.sleep(10)
        self.tb.stop()
        self.tb.wait()

        # get current working folder
        base = os.getcwd()
        # file with output data that is expected
        file_expected = base + "/../../test_files/64_result.txt"

        # set the written data file
        file_result = base + "/../../test_files/tx_64_result.txt"
        result_data = dst.data()
        f = open(file_result, "w")
        f.write(str(result_data))
        f.close()

        # compare the actual files
        self.assertTrue(
            filecmp.cmp(
                file_expected,
                file_result),
            'Error test failed, expected data and actual data are not the same')


if __name__ == '__main__':
    gr_unittest.run(qa_tx)
