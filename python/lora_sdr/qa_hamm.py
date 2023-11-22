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

def int_to_bool(value, num_bits):

    return [(value >> i) & 1 for i in range(num_bits - 1, -1, -1)]
   

class qa_hamm(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001_function_test(self):

        sf = 7
        cr = 2
        src_data = (1,1,0,2,3)

        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        blocks_vector_source_x_0 = blocks.vector_source_b(src_data, False, 1, [])
        blocks_vector_sink_1_0 = blocks.vector_sink_b(1, 1024)

        self.tb.connect((blocks_vector_source_x_0, 0), (lora_sdr_hamming_enc_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (blocks_vector_sink_1_0, 0))
        self.tb.run()

        result_data = blocks_vector_sink_1_0.data()
        ref_data = [139, 139, 0, 78, 197]

        # generate reference data
        data_bin = []
        ref_out = [0] * len(src_data)
        p0, p1, p2, p3, p4 = False, False, False, False, False
        m_cnt = 0

        for i in range(len(src_data)):
            #ifdef GRLORA_DEBUG
            print(f'{src_data[i]:02X}   ', end='')
            #endif
            
            cr_app = 4 if m_cnt < sf - 2 else cr
            data_bin = int_to_bool(src_data[i], 4)
            print(data_bin)

            # the data_bin is msb first
            if cr_app != 1:
                p0 = data_bin[3] ^ data_bin[2] ^ data_bin[1]
                p1 = data_bin[2] ^ data_bin[1] ^ data_bin[0]
                p2 = data_bin[3] ^ data_bin[2] ^ data_bin[0]
                p3 = data_bin[3] ^ data_bin[1] ^ data_bin[0]

                # we put the data LSB first and append the parity bits
                ref_out[i] = ((data_bin[3] << 7) | (data_bin[2] << 6) | (data_bin[1] << 5) |
                                (data_bin[0] << 4) | (p0 << 3) | (p1 << 2) | (p2 << 1) | p3) >> (4 - cr_app)
            else:
                # coding rate = 4/5, add a parity bit
                p4 = data_bin[0] ^ data_bin[1] ^ data_bin[2] ^ data_bin[3]
                ref_out[i] = ((data_bin[3] << 4) | (data_bin[2] << 3) | (data_bin[1] << 2) |
                                (data_bin[0] << 1) | p4)

            #ifdef GRLORA_DEBUG
            print(ref_out[i])
            #endif
            m_cnt += 1


        self.assertEqual(ref_out, result_data)
        
    

if __name__ == '__main__':
    gr_unittest.run(qa_hamm)
