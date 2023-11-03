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


class qa_modulate(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001(self):

        src_data = (15,18,1,1,9,1,44)
        
        sf = 7
        samp_rate = 500000
        preamb_len = 8

        bw = 125000

        blocks_file_source = blocks.file_source(gr.sizeof_int*1, '/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx_no_mod/ref_tx_sf7_cr2.bin', False, 0, 0)
        #qa_ref_tx_no_mod/ref_tx_sf7_cr2.bin', False, 0, 0)
        blocks_file_source.set_begin_tag(pmt.PMT_NIL)
        #blocks_vector_source = blocks.vector_source_i(src_data, False, 1, [])
        blocks_throttle = blocks.throttle(gr.sizeof_gr_complex*1, (samp_rate*10),True)
        lora_sdr_modulate = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),8)
        blocks_vector_sink = blocks.vector_sink_c(1, 1024)
        #dst = blocks.null_sink(gr.sizeof_char)
        self.tb.connect((blocks_file_source, 0), (lora_sdr_modulate, 0))
        self.tb.connect((lora_sdr_modulate, 0), (blocks_throttle, 0))
        self.tb.connect((blocks_throttle, 0), (blocks_vector_sink, 0))
     
        self.tb.run()
        #self.tb.run()
        result_data = blocks_vector_sink.data()
        #print(result_data)
        #f = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_flow_mod/ref_flow_mod_sf7_cr2.bin","rb")
        f = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_mod/ref_tx_sf7_cr2.bin","rb")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()
        self.assertEqual(result_data, list(ref_data))

        
    

    

if __name__ == '__main__':
    gr_unittest.run(qa_modulate)
