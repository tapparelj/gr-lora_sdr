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

def make_tag_string(key, value, offset, srcid=None):
    tag = gr.tag_t()
    tag.key = pmt.string_to_symbol(key)
    # Convert elements of 'value' to strings before using string_to_symbol
    value_strings = [str(v) for v in value]
    tag.value = pmt.string_to_symbol(value_strings[0])
    tag.offset = offset
    if srcid is not None:
        tag.srcid = pmt.to_pmt(srcid)
    return tag

def crc16(crc_value, new_byte):
    # Assuming new_byte is a character
    byte_value = ord(new_byte) & 0xFF
  
    for i in range(8):
        if ((crc_value & 0x8000) >> 8) ^ (byte_value & 0x80):
            crc_value = (crc_value << 1) ^ 0x1021
        else:
            crc_value = (crc_value << 1)
        byte_value <<= 1
        byte_value = byte_value & 0xFF
       

    return crc_value & 0xffff


def calculate_crc(payload):
    crc = 0x0000
    payload_len = len(payload)

    # Calculate CRC on the N-2 first data bytes using Poly=1021 Init=0000
    for i in range(payload_len - 2):
        
        crc = crc16(crc, str(payload[i]))
    crc_nibbles = [
        (crc & 0x000F),
        ((crc & 0x00F0) >> 4),
        ((crc & 0x0F00) >> 8),
        ((crc & 0xF000) >> 12)
    ]

    return crc_nibbles

class qa_add_crc(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        sf = 7

        has_crc = True
        cr = 2
        payload_len = 13

        # use output of add_header block
        src_data_str = "31364" # random input source
        src_data_int = [3,1,3,6,4]
        src_data = [0, 4, 5, 0, 2, 15, 12, 15, 3, 15, 10, 15, 12] # output of use output of add_header block

        src_tags = [make_tag('frame_len',payload_len,0,'src_data'),make_tag_string('payload_str', src_data_str, 0,'src')] 

        lora_sdr_add_crc = lora_sdr.add_crc(has_crc)
        blocks_vector_source = blocks.vector_source_b(src_data, False, 1, src_tags)
        blocks_vector_sink = blocks.vector_sink_b(1, 2048)

        self.tb.connect((blocks_vector_source, 0), (lora_sdr_add_crc , 0))
        self.tb.connect((lora_sdr_add_crc , 0), (blocks_vector_sink, 0))
        self.tb.run()

        result_data = blocks_vector_sink.data()
        # generate crc 
        ref_crc = calculate_crc(src_data_int)
        ref_out = src_data + ref_crc
        
        self.assertEqual(result_data, ref_out)

    
if __name__ == '__main__':
    gr_unittest.run(qa_add_crc)
