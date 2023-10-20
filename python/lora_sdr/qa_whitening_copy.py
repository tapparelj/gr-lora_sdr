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

# from gnuradio import blocks
try:
  from gnuradio.lora_sdr import whitening
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    from gnuradio.lora_sdr import whitening

class qa_whitening(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001(self):

        src_data = (0,1,1,0,0,0,0,0,0,0,44)
        expected_data = [0] * (len(src_data) - 1)
        
        for i in range(len(src_data)-1):
            expected_data[i] = (src_data[i]^code[i])
            print(hex(expected_data[i]))


        # expected_result =144
        src = blocks.vector_source_b(src_data, False, 1,[])
        #src = blocks.file_source(gr.sizeof_char*1, '/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt', False, 0, 0)
        lora_sdr_whitening_0 = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()
        #dst = blocks.null_sink(gr.sizeof_char)
        self.tb.connect((src, 0), (lora_sdr_whitening_0, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (dst,0))
     
        # result_data = dst.data()
        self.tb.run()
        result_data = dst.data()
        
        for i in range(int(len(result_data)/2)):
            result = result_data[2*i] | (result_data[2*i+1]<<4)
            print(hex(result))    
            self.assertEqual(result, expected_data[i])

    def test_002_whitening_test(self):
        src_data = (0,0,0,0,0,0,0,0,0,0,44)
        expected_data = [0] * (len(src_data) - 1)
        
        for i in range(len(src_data)-1):
            expected_data[i] = (src_data[i]^code[i])
            print(hex(expected_data[i]))


        # expected_result =144
        src = blocks.vector_source_b(src_data, False, 1,[])
        #src = blocks.file_source(gr.sizeof_char*1, '/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt', False, 0, 0)
        lora_sdr_whitening_0 = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()
        #dst = blocks.null_sink(gr.sizeof_char)
        self.tb.connect((src, 0), (lora_sdr_whitening_0, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (dst,0))
     
        # result_data = dst.data()
        self.tb.run()
        result_data = dst.data()
        
        for i in range(int(len(result_data)/2)):
            result = result_data[2*i] | (result_data[2*i+1]<<4)
            print(hex(result))    
            self.assertEqual(result, expected_data[i])


if __name__ == '__main__':
    gr_unittest.run(qa_whitening)
