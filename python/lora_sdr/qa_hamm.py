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
   

class qa_hamm(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

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
        clk_offset = 0
        center_freq = 868.1e6
        bw = 125000
        SNRdB = -5
        src_data = (1,1,0,2,3)

        ##################################################
        # Blocks
        ##################################################
        ##################################################
        # Blocks
        ##################################################
        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        blocks_vector_source_x_0 = blocks.vector_source_b(src_data, False, 1, [])
        blocks_vector_sink_1_0 = blocks.vector_sink_b(1, 1024)


        ##################################################
        # Connections
        ##################################################
        self.tb.connect((blocks_vector_source_x_0, 0), (lora_sdr_hamming_enc_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (blocks_vector_sink_1_0, 0))

        self.tb.run()
        result_data = blocks_vector_sink_1_0.data()
        ref_data = [139, 139, 0, 78, 197]

        #print(result_data)


        self.assertEqual(ref_data, result_data)
        
    

    

if __name__ == '__main__':
    gr_unittest.run(qa_hamm)
