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


# from gnuradio import blocks
try:
    import gnuradio.lora_sdr as lora_sdr
   
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
   

class qa_gray_demap(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001_function_test(self):

        sf = 7
        src_data = (0, 1, 2)

        lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        blocks_vector_source_x_0 = blocks.vector_source_i(src_data, False, 1, [])
        blocks_vector_sink_x_0 = blocks.vector_sink_i(1, 1024)

        self.tb.connect((blocks_vector_source_x_0, 0), (lora_sdr_gray_demap_0, 0))
        self.tb.connect((lora_sdr_gray_demap_0, 0), (blocks_vector_sink_x_0, 0))

        self.tb.run()
        result_data = blocks_vector_sink_x_0.data()
        #print(result_data)
        ref_data = [1,2,4]

        # generate reference data
        ref_data = [0] * len(src_data)
        for i in range(len(src_data)):
            ref_data[i] = src_data[i]
            for j in range(1, sf):
                ref_data[i]=ref_data[i]^(src_data[i]>>j)
            ref_data[i] = ((ref_data[i]+1) % (1 << sf))

        self.assertEqual(ref_data, result_data)

if __name__ == '__main__':
    gr_unittest.run(qa_gray_demap)
