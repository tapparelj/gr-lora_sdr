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
def make_tag(key, value, offset, srcid=None):
    tag = gr.tag_t()
    tag.key = pmt.string_to_symbol(key)
    tag.value = pmt.to_pmt(value)
    tag.offset = offset
    if srcid is not None:
        tag.srcid = pmt.to_pmt(srcid)
    return tag

class qa_add_crc(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        sf = 7

        has_crc = True
        cr = 2
        payload_len = 6
   
        src_data = (14,15,15,15,15,15)
        src_data_str = str(src_data)

        src_tags = [make_tag('frame_len',payload_len,0,'src_data'),make_tag('payload_str', src_data_str, 0,'src')] 

        lora_sdr_add_crc = lora_sdr.add_crc(has_crc)
        blocks_vector_source = blocks.vector_source_b(src_data, True, 1, src_tags)
        blocks_vector_sink = blocks.vector_sink_b(1, 2048)
        relative_out_path = "qa_ref/temp/add_crc6_"+str(sf)+"_cr"+str(cr)+".bin"

        self.tb.connect((blocks_vector_source, 0), (lora_sdr_add_crc , 0))
        self.tb.connect((lora_sdr_add_crc , 0), (blocks_vector_sink, 0))
        self.tb.run()

        result_data = blocks_vector_sink.data()
        # Load ref files
        print(result_data)

        

       

           
if __name__ == '__main__':
    gr_unittest.run(qa_add_crc)
