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
  from gnuradio.lora_sdr import whitening
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    from gnuradio.lora_sdr import whitening

def make_tag(key, value, offset, srcid=None):
    tag = gr.tag_t()
    tag.key = pmt.string_to_symbol(key)
    tag.value = pmt.to_pmt(value)
    tag.offset = offset
    if srcid is not None:
        tag.srcid = pmt.to_pmt(srcid)
    return tag
def compare_tags(a, b):
    return a.offset == b.offset and pmt.equal(a.key, b.key) and \
        pmt.equal(a.value, b.value) and pmt.equal(a.srcid, b.srcid)

class CustomSourceBlock(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self, name="Custom Source Block", in_sig=None, out_sig=[np.byte])

    def work(self, input_items, output_items):
        num_output_items = len(output_items[0])

        # Put your code here to fill the output_items...

        # Make a new tag on the middle element every time work is called
        count = self.nitems_written(0) + num_output_items / 2
        key = pmt.string_to_symbol("example_key")
        value = pmt.string_to_symbol("example_value")
        self.add_item_tag(0, count, key, pmt.string_to_symbol("example_value"))
        return num_output_items



class qa_whitening(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def combine(self, result_data):
        return [result_data[2 * i] | (result_data[2 * i + 1] << 4) for i in range(int(len(result_data) / 2))]


    def test_001_vector_source(self):

        src_data = (1,1,44) # In ASCII, 44 represents comma. The block stops when it meets the separator ','
        expected_data = [0] * (len(src_data) - 1)
        expected_data = [src_data[i] ^ code[i] for i in range(len(src_data) - 1)]
        
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data()
        print(result_data)
        result_tags = dst.tags()
        print(result_tags)
        result_data = self.combine(result_data)
        print(result_data)

        
        self.assertEqual(result_data, expected_data)

    def test_002_file_source(self):

        file_path = '/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt'
        src = blocks.file_source(gr.sizeof_char*1, file_path, False, 0, 0)
        
        with open(file_path, "r") as file:
            file_contents = file.read()
        
        input_string = file_contents.split(",")
        result_segments = []
        for i in range(len(input_string)):
           
            for word, xor_value in zip(input_string[i], code):
                # Convert the segment and XOR value to integers
                word_xor = hex(ord(word) ^ xor_value)
                result_segments.append(word_xor) 

        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data()
        result_data = [hex(result_data[2 * i] | (result_data[2 * i + 1] << 4)) for i in range(int(len(result_data) / 2))]

        self.assertEqual(result_data, result_segments)

    def test_003_whitening_sequence_validation(self):

        src_data = [255] * 255 + [44] # In ASCII, 44 represents comma. The block stops when it meets the separator ','
       
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data()
        result_data = self.combine(result_data)
        flipped_code = [byte ^ 0xFF for byte in code]
        self.assertEqual(result_data, flipped_code)

    def test_004_edge_test_empty_input(self):

        src_data = ()
        expected_data = [0] * (len(src_data) - 1)
        expected_data = [src_data[i] ^ code[i] for i in range(len(src_data) - 1)]
        
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data()
        result_data = self.combine(result_data)
        
        self.assertEqual(result_data, expected_data)

    def test_005_is_hex(self): # input should be even length

        file_path = '/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source_ishex.txt'
        src = blocks.file_source(gr.sizeof_char*1, file_path, False, 0, 0)
        with open(file_path, "r") as file:
            file_contents = file.read()
        input_string = file_contents.split(",")
        result_segments = []
        for i in range(len(input_string)):
            segments = [input_string[i][j:j+2] for j in range(0, len(input_string[i]), 2)]
            
            for segment, xor_value in zip(segments, code):
                # Convert the segment and XOR value to integers
                segment_int = int(segment, 16)
                
                result_int = segment_int ^ xor_value
                result_segments.append(result_int)        

        lora_sdr_whitening = whitening(True,False,',','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data()
        result_data = self.combine(result_data)
    
        self.assertEqual(result_data, result_segments)

    def test_006_use_tag_function_test(self):

        src_data = (1,1,1,1,1,1,1)
        src_tags = [make_tag('packet_len',7 ,0,'src_data')]
        expected_data = [0] * (len(src_data))
        expected_data = [src_data[i] ^ code[i] for i in range(len(src_data))]
        
        src = blocks.vector_source_b(src_data, False, 1, src_tags)
        lora_sdr_whitening = whitening(False,True,' ','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data() 
        result_tags = dst.tags()
        result_data = self.combine(result_data)

        self.assertEqual(result_data, expected_data)

    def test_007_use_multiple_tags(self):

        src_data = [np.byte(x) for x in range(112)]
        src_tags = [make_tag('packet_len',16 ,0,'src_data'), make_tag('packet_len',32 ,16,'src_data'),make_tag('packet_len',64 ,48,'src_data')]
        expected_data = [0] * (len(src_data))
        for i in range(16):
            expected_data[i] = src_data[i] ^ code[i]
        for i in range(16,48):
            expected_data[i] = src_data[i] ^ code[i-16]
        for i in range(48,112):
            expected_data[i] = src_data[i] ^ code[i-48]
        
        src = blocks.vector_source_b(src_data, False, 1, src_tags)
        lora_sdr_whitening = whitening(False,True,' ','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data() 
        result_data = self.combine(result_data)

        self.assertEqual(result_data, expected_data)
    


if __name__ == '__main__':
    gr_unittest.run(qa_whitening)
