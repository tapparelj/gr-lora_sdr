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

class qa_add_header(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        sf = 7
        samp_rate = 500000
        preamb_len = 8
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        payload_len = 6
        bw = 125000
        src_data = (14,15,15,15,15,15)
        src = (1,1)
        src_tags = [make_tag('frame_len',payload_len,0,'src_data'),make_tag('payload_str',src_data,0,'src')] 

        lora_sdr_header = lora_sdr.header(impl_head, has_crc, cr)
        blocks_vector_source = blocks.vector_source_b(src_data, True, 1, src_tags)
        blocks_vector_sink = blocks.vector_sink_b(1, 1024)
        relative_out_path = "qa_ref/temp/add_header6_"+str(sf)+"_cr"+str(cr)+".bin"
        output_path = os.path.join(script_dir, relative_out_path)
        blocks_file_sink = blocks.file_sink(gr.sizeof_char*1, output_path, False)
        blocks_file_sink.set_unbuffered(False)

        self.tb.connect((blocks_vector_source, 0), (lora_sdr_header, 0))
        self.tb.connect((lora_sdr_header, 0), (blocks_vector_sink, 0))
        self.tb.run()


        f = open(output_path,"r")
        ref_data = np.fromfile(f, dtype=np.int32)
        f.close()
        print(list(ref_data))


        # calculate the header
        m_header = [0] * 5
        m_header[0] = int(payload_len/2) >> 4
        m_header[1] = int(payload_len/2) & 0x0F
        m_header[2] = (cr << 1) | has_crc

        c4 = (m_header[0] & 0b1000) >> 3 ^ (m_header[0] & 0b0100) >> 2 ^ (m_header[0] & 0b0010) >> 1 ^ (m_header[0] & 0b0001)
        c3 = (m_header[0] & 0b1000) >> 3 ^ (m_header[1] & 0b1000) >> 3 ^ (m_header[1] & 0b0100) >> 2 ^ (m_header[1] & 0b0010) >> 1 ^ (m_header[2] & 0b0001)
        c2 = (m_header[0] & 0b0100) >> 2 ^ (m_header[1] & 0b1000) >> 3 ^ (m_header[1] & 0b0001) ^ (m_header[2] & 0b1000) >> 3 ^ (m_header[2] & 0b0010) >> 1
        c1 = (m_header[0] & 0b0010) >> 1 ^ (m_header[1] & 0b0100) >> 2 ^ (m_header[1] & 0b0001) ^ (m_header[2] & 0b0100) >> 2 ^ (m_header[2] & 0b0010) >> 1 ^ (m_header[2] & 0b0001)
        c0 = (m_header[0] & 0b0001) ^ (m_header[1] & 0b0010) >> 1 ^ (m_header[2] & 0b1000) >> 3 ^ (m_header[2] & 0b0100) >> 2 ^ (m_header[2] & 0b0010) >> 1 ^ (m_header[2] & 0b0001)

        m_header[3] = c4
        m_header[4] = c3 << 3 | c2 << 2 | c1 << 1 | c0


        result_data = blocks_vector_sink.data()
        # Load ref files
        #print(result_data)

        self.assertEqual(result_data[:5], m_header)

           
if __name__ == '__main__':
    gr_unittest.run(qa_add_header)
