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
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

# from gnuradio import blocks
try:
    import gnuradio.lora_sdr as lora_sdr
   
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
   

class qa_fft_demod(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001_function_test(self):

        soft_decoding = False
        src_data = [(-74.8629 - 63.2502j)] *356

        lora_sdr_fft_demod_0 = lora_sdr.fft_demod(soft_decoding, False)
        blocks_vector_source_x_0 = blocks.vector_source_c(src_data, False, 1, [])
        blocks_vector_sink_x_0 = blocks.vector_sink_s(1, 1024)

        self.tb.connect((blocks_vector_source_x_0, 0), (lora_sdr_fft_demod_0, 0))
        self.tb.connect((lora_sdr_fft_demod_0, 0), (blocks_vector_sink_x_0, 0))

        self.tb.run()
        result_data = blocks_vector_sink_x_0.data()
        print(result_data)
        

        #print(result_data)


        #self.assertEqual(ref_data, result_data)
    def test_002_function_test(self):

        soft_decoding = False
        lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, False)
        blocks_vector_sink_x_1 = blocks.vector_sink_s(1, 1024)
        path = "qa_ref/temp/ref_fft_demod_input.bin"

        input_path = os.path.join(script_dir, path)
       
        blocks_file_source_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, input_path, False, 0, 0)
        blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)

        self.tb.connect((blocks_file_source_0_1, 0), (lora_sdr_fft_demod_0, 0))
        self.tb.connect((lora_sdr_fft_demod_0, 0), (blocks_vector_sink_x_1, 0))

        self.tb.run()
        result_data = blocks_vector_sink_x_1.data()
        #print(result_data)
        


if __name__ == '__main__':
    gr_unittest.run(qa_fft_demod)
