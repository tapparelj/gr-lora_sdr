#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                     GNU GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
#
#  Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
#  Everyone is permitted to copy and distribute verbatim copies
#  of this license document, but changing it is not allowed.


from gnuradio import gr, gr_unittest
from gnuradio import analog
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np
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

class qa_tx_buffer(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    

    def test_001_function_test(self):

        src_data = (0,1,0,0,0,44)
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
        src0 = blocks.vector_source_b(src_data, False, 1, [])
        src1 = blocks.vector_source_c(200 * [1])
        src2 = blocks.vector_source_c(200 * [2])
        lora_sdr_whitening_0 = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),preamb_len)
        lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro, 125000)
        lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        blocks_vector_sink_x_0 = blocks.vector_sink_c(1, 1024)
        blocks_vector_sink_x_1 = blocks.vector_sink_c(1, 1024)
        blocks_patterned_interleaver_0 = blocks.patterned_interleaver(gr.sizeof_gr_complex*1, [0,1])
        blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        relative_path = "../../data/GRC_default/example_tx_source.txt"
        input_path = os.path.join(script_dir, relative_path)
        blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, input_path, False, 0, 0)
        blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)
        analog_const_source_x_0 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0)
        relative_out_path = "qa_ref/temp/ref_buffer_test.bin"
        output_path = os.path.join(script_dir, relative_out_path)
        blocks_file_sink = blocks.file_sink(gr.sizeof_gr_complex*1, output_path, False)
        blocks_file_sink.set_unbuffered(False)

        self.tb.connect((analog_const_source_x_0, 0), (blocks_patterned_interleaver_0, 0))
        self.tb.connect((blocks_file_source_0_0, 0), (lora_sdr_whitening_0, 0))
        self.tb.connect((blocks_patterned_interleaver_0, 0), (blocks_null_sink_0, 0))
        self.tb.connect((lora_sdr_add_crc_0, 0), (lora_sdr_hamming_enc_0, 0))
        self.tb.connect((lora_sdr_gray_demap_0, 0), (lora_sdr_modulate_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (lora_sdr_interleaver_0, 0))
        self.tb.connect((lora_sdr_header_0, 0), (lora_sdr_add_crc_0, 0))
        self.tb.connect((lora_sdr_interleaver_0, 0), (lora_sdr_gray_demap_0, 0))
        self.tb.connect((lora_sdr_modulate_0, 0), (blocks_patterned_interleaver_0, 1))
        self.tb.connect((lora_sdr_modulate_0, 0), (blocks_file_sink, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (lora_sdr_header_0, 0))
        self.tb.run()

        # Load ref files
        relative_ref_path = "qa_ref/temp/ref_buffer.bin"
        reference_path = os.path.join(script_dir, relative_ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()
        #print(result_data)
        relative_result_path = "qa_ref/temp/ref_buffer_test.bin"
        reference_test_path = os.path.join(script_dir, relative_result_path)
        f1 = open(reference_test_path,"r")
        result_data = np.fromfile(f1, dtype=np.complex64)
        f1.close()

        

        self.assertEqual(list(result_data), list(ref_data))
    

    

if __name__ == '__main__':
    gr_unittest.run(qa_tx_buffer)
