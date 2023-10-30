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
from table import code
import pmt
import numpy as np


# from gnuradio import blocks
try:
    import gnuradio.lora_sdr as lora_sdr
   
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
   

class qa_rx(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001(self):

        soft_decoding = False
        sf = 7
        samp_rate = 500000
        preamb_len = 8
        pay_len = 16
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        clk_offset = 0
        center_freq = 868.1e6
        bw = 125000
        SNRdB = -5

        ##################################################
        # Blocks
        ##################################################
        lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro, True)
        lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], (int(samp_rate/bw)),preamb_len)
        lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, False)
        lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        lora_sdr_crc_verif_0 = lora_sdr.crc_verif( True, False)
        input_file_path = "/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx/ref_tx_sf{}_cr{}.bin".format(sf, cr)
        blocks_file_source_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, input_file_path, False, 0, 0)
        blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)
        # output_file_path = "/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/temp/ref_rx_sf{}_cr{}.bin".format(sf, cr)
        # blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_char*1, output_file_path, False)
        # blocks_file_sink_0_0.set_unbuffered(False)
        blocks_vector_sink_x_1 = blocks.vector_sink_b(1, 1024)


        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((lora_sdr_header_decoder_0, 'frame_info'), (lora_sdr_frame_sync_0, 'frame_info'))
        self.tb.connect((blocks_file_source_0_1, 0), (lora_sdr_frame_sync_0, 0))
        #self.tb.connect((lora_sdr_crc_verif_0, 0), (blocks_file_sink_0_0, 0))
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

        f = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_rx/ref_rx_sf"+str(sf)+"_cr"+str(cr)+".bin","r")
        ref_data = np.fromfile(f, dtype=np.int32)
        f.close()
        with open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_rx/ref_rx_sf"+str(sf)+"_cr"+str(cr)+".bin", "rb") as f2:
            binary_data = f2.read()

        grouped_data = [binary_data[i:i+1] for i in range(0, len(binary_data), 1)]

        # Convert the grouped data to integers
        grouped_integers = [int.from_bytes(group, byteorder="big") for group in grouped_data]
        # f_t = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/temp/ref_rx_sf"+str(sf)+"_cr"+str(cr)+".bin","r")
        # result_data = np.fromfile(f_t, dtype=np.int32)
        # f_t.close()

        self.assertEqual(grouped_integers, result_data)
        
    

    

if __name__ == '__main__':
    gr_unittest.run(qa_rx)
