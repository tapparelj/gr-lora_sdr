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
from gnuradio import filter
from gnuradio.filter import firdes
import ast

class qa_rx(gr_unittest.TestCase):

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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/1_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/2_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/3_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/4_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/5_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/6_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/7_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/8_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_9(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/9_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_10(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/10_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_11(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/11_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_12(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/12_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_13(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/13_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_14(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/14_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_15(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/15_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_16(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/16_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_17(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/17_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_18(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/18_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_19(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/19_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_20(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/20_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_21(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/21_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_22(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/22_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_23(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/23_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_24(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/24_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_25(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/25_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_26(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/26_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_27(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/27_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_28(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/28_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_29(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/29_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_30(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/30_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_31(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/31_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_32(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/32_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/33_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/34_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/35_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/36_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/37_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/38_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/39_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

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
        self.impl_head = impl_head = True
        self.has_crc = has_crc = True
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/40_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_41(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/41_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_42(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/42_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_43(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/43_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_44(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/44_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_45(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/45_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_46(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/46_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_47(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/47_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_48(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/48_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_49(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/49_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_50(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/50_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_51(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/51_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_52(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/52_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_53(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/53_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_54(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/54_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_55(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/55_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_56(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/56_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_57(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/57_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_58(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/58_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_59(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/59_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_60(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/60_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_61(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/61_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_62(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/62_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_63(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/63_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")

    def test_64(self):
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=4,
            decimation=1,
            taps=None,
            fractional_bw=None)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(
            impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(
            samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.blocks_message_debug_0 = blocks.message_debug()

        # get the writen file
        base = os.getcwd()
        file_result = base + "/../../test_files/64_result.txt"
        f = open(file_result, "r")
        vector = f.read()
        f.close()
        # transform vector string from file to the right format
        vector = ast.literal_eval(vector)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(
            vector, False, 1, [])

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'),
                            (self.blocks_message_debug_0, 'store'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_deinterleaver_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_dewhitening_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_fft_demod_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_hamming_dec_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_frame_sync_0,
             'new_frame'),
            (self.lora_sdr_header_decoder_0,
             'new_frame'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_crc_verif_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'),
                            (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_dewhitening_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0,
             'pay_len'),
            (self.lora_sdr_frame_sync_0,
             'pay_len'))
        self.tb.msg_connect(
            (self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0),
                        (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0),
                        (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0),
                        (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0),
                        (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0),
                        (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0),
                        (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0),
                        (self.lora_sdr_dewhitening_0, 0))
        self.tb.connect((self.rational_resampler_xxx_0, 0),
                        (self.lora_sdr_frame_sync_0, 0))
        self.tb.connect((self.blocks_vector_source_x_0, 0),
                        (self.rational_resampler_xxx_0, 0))

        # run the flowgraph
        self.tb.run()
        # get the message from the store port of the message debug printer
        msg = self.blocks_message_debug_0.get_message(0)

        # #self.tb.run()
        # self.tb.start()
        # time.sleep(10)
        # self.tb.stop()
        # self.tb.wait()
        self.assertMultiLineEqual(
            src_data, msg, msg="Error decoded data is not the same as input data")


if __name__ == '__main__':
    gr_unittest.run(qa_rx)
