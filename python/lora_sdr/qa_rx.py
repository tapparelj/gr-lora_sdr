#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                     GNU GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
#
#  Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
#  Everyone is permitted to copy and distribute verbatim copies
#  of this license document, but changing it is not allowed.


from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np
import time
import os
import sys


# from gnuradio import blocks
try:
    import gnuradio.lora_sdr as lora_sdr
   
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))

script_dir = os.path.dirname(os.path.abspath(__file__))

class qa_rx(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_function_test(self):

        soft_decoding = False
        sf = 7
        samp_rate = 500000
        preamb_len = 8
        pay_len = 16
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        center_freq = 868.1e6
        bw = 125000

        lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro, True)
        lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], (int(samp_rate/bw)),preamb_len)
        lora_sdr_fft_demod_0 = lora_sdr.fft_demod(soft_decoding, False)
        lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        lora_sdr_crc_verif_0 = lora_sdr.crc_verif(True, False)
        relative_path = "qa_ref/qa_ref_tx/ref_tx_sf{}_cr{}.bin".format(sf, cr)
        input_file_path = os.path.join(script_dir, relative_path)
        blocks_file_source_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, input_file_path, False, 0, 0)
        blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)
        blocks_vector_sink_x_1 = blocks.vector_sink_b(1, 1024)

        self.tb.msg_connect((lora_sdr_header_decoder_0, 'frame_info'), (lora_sdr_frame_sync_0, 'frame_info'))
        self.tb.connect((blocks_file_source_0_1, 0), (lora_sdr_frame_sync_0, 0))
        self.tb.connect((lora_sdr_deinterleaver_0, 0), (lora_sdr_hamming_dec_0, 0))
        self.tb.connect((lora_sdr_dewhitening_0, 0), (lora_sdr_crc_verif_0, 0))
        self.tb.connect((lora_sdr_fft_demod_0, 0), (lora_sdr_gray_mapping_0, 0))
        self.tb.connect((lora_sdr_frame_sync_0, 0), (lora_sdr_fft_demod_0, 0))
        self.tb.connect((lora_sdr_gray_mapping_0, 0), (lora_sdr_deinterleaver_0, 0))
        self.tb.connect((lora_sdr_hamming_dec_0, 0), (lora_sdr_header_decoder_0, 0))
        self.tb.connect((lora_sdr_header_decoder_0, 0), (lora_sdr_dewhitening_0, 0))
        self.tb.connect((lora_sdr_crc_verif_0, 0), (blocks_vector_sink_x_1, 0))
        self.tb.run()

        result_data = blocks_vector_sink_x_1.data()
        # Load ref files
        relative_path2 = "qa_ref/qa_ref_rx/ref_rx_sf{}_cr{}.bin".format(sf, cr)
        ref_file_path = os.path.join(script_dir, relative_path2)
        with open(ref_file_path, "rb") as f2:
            binary_data = f2.read()
        grouped_data = [binary_data[i:i+1] for i in range(0, len(binary_data), 1)]
        grouped_integers = [int.from_bytes(group, byteorder="big") for group in grouped_data]

        self.assertEqual(grouped_integers, result_data)

    def test_002_edge_test(self):

        soft_decoding = False
        sf = 11
        samp_rate = 500000
        preamb_len = 8
        pay_len = 16
        ldro = False
        impl_head = False
        has_crc = True
        cr = 5
        center_freq = 868.1e6
        bw = 125000

        lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro, True)
        lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], (int(samp_rate/bw)),preamb_len)
        lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, False)
        lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        lora_sdr_crc_verif_0 = lora_sdr.crc_verif( True, False)
        relative_path = "qa_ref/qa_ref_tx/ref_tx_sf{}_cr{}.bin".format(sf, cr)
        input_file_path = os.path.join(script_dir, relative_path)
        blocks_file_source_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, input_file_path, False, 0, 0)
        blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)
        blocks_vector_sink_x_1 = blocks.vector_sink_b(1, 1024)

        self.tb.msg_connect((lora_sdr_header_decoder_0, 'frame_info'), (lora_sdr_frame_sync_0, 'frame_info'))
        self.tb.connect((blocks_file_source_0_1, 0), (lora_sdr_frame_sync_0, 0))
        self.tb.connect((lora_sdr_deinterleaver_0, 0), (lora_sdr_hamming_dec_0, 0))
        self.tb.connect((lora_sdr_dewhitening_0, 0), (lora_sdr_crc_verif_0, 0))
        self.tb.connect((lora_sdr_fft_demod_0, 0), (lora_sdr_gray_mapping_0, 0))
        self.tb.connect((lora_sdr_frame_sync_0, 0), (lora_sdr_fft_demod_0, 0))
        self.tb.connect((lora_sdr_gray_mapping_0, 0), (lora_sdr_deinterleaver_0, 0))
        self.tb.connect((lora_sdr_hamming_dec_0, 0), (lora_sdr_header_decoder_0, 0))
        self.tb.connect((lora_sdr_header_decoder_0, 0), (lora_sdr_dewhitening_0, 0))
        self.tb.connect((lora_sdr_crc_verif_0, 0), (blocks_vector_sink_x_1, 0))
        self.tb.run()

        result_data = blocks_vector_sink_x_1.data()
        # Load ref files
        relative_path2 = "qa_ref/qa_ref_rx/ref_rx_sf{}_cr{}.bin".format(sf, cr)
        ref_file_path = os.path.join(script_dir, relative_path2)
        with open(ref_file_path, "rb") as f2:
            binary_data = f2.read()
        grouped_data = [binary_data[i:i+1] for i in range(0, len(binary_data), 1)]
        grouped_integers = [int.from_bytes(group, byteorder="big") for group in grouped_data]

        self.assertEqual(grouped_integers, result_data)

    def test_003_soft_decoding(self):

        soft_decoding = False
        sf = 11
        samp_rate = 500000
        preamb_len = 8
        pay_len = 16
        ldro = False
        impl_head = False
        has_crc = True
        cr = 5
        center_freq = 868.1e6
        bw = 125000

        lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro, True)
        lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], (int(samp_rate/bw)),preamb_len)
        lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, False)
        lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        lora_sdr_crc_verif_0 = lora_sdr.crc_verif( True, False)
        relative_path = "qa_ref/qa_ref_tx/ref_tx_sf{}_cr{}.bin".format(sf, cr)
        input_file_path = os.path.join(script_dir, relative_path)
        blocks_file_source_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, input_file_path, False, 0, 0)
        blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)
        blocks_vector_sink_x_1 = blocks.vector_sink_b(1, 1024)

        self.tb.msg_connect((lora_sdr_header_decoder_0, 'frame_info'), (lora_sdr_frame_sync_0, 'frame_info'))
        self.tb.connect((blocks_file_source_0_1, 0), (lora_sdr_frame_sync_0, 0))
        self.tb.connect((lora_sdr_deinterleaver_0, 0), (lora_sdr_hamming_dec_0, 0))
        self.tb.connect((lora_sdr_dewhitening_0, 0), (lora_sdr_crc_verif_0, 0))
        self.tb.connect((lora_sdr_fft_demod_0, 0), (lora_sdr_gray_mapping_0, 0))
        self.tb.connect((lora_sdr_frame_sync_0, 0), (lora_sdr_fft_demod_0, 0))
        self.tb.connect((lora_sdr_gray_mapping_0, 0), (lora_sdr_deinterleaver_0, 0))
        self.tb.connect((lora_sdr_hamming_dec_0, 0), (lora_sdr_header_decoder_0, 0))
        self.tb.connect((lora_sdr_header_decoder_0, 0), (lora_sdr_dewhitening_0, 0))
        self.tb.connect((lora_sdr_crc_verif_0, 0), (blocks_vector_sink_x_1, 0))
        self.tb.run()

        result_data = blocks_vector_sink_x_1.data()
        # Load ref files
        relative_path2 = "qa_ref/qa_ref_rx/ref_rx_sf{}_cr{}.bin".format(sf, cr)
        ref_file_path = os.path.join(script_dir, relative_path2)
        with open(ref_file_path, "rb") as f2:
            binary_data = f2.read()
        grouped_data = [binary_data[i:i+1] for i in range(0, len(binary_data), 1)]
        grouped_integers = [int.from_bytes(group, byteorder="big") for group in grouped_data]

        self.assertEqual(grouped_integers, result_data)
    

if __name__ == '__main__':
    gr_unittest.run(qa_rx)
