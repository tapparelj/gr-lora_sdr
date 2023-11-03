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

    def combine(self, result_data):
        return [result_data[2 * i] | (result_data[2 * i + 1] << 4) for i in range(int(len(result_data) / 2))]

    def test_001_vector_source(self):

        src_data = (0,1,1,0,25,0,0,0,0,0,44)
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

        src_data = [0] * 255 + [44]
       
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data()
        result_data = self.combine(result_data)
            
        self.assertEqual(result_data, code)           

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

    def test_005_edge_test_large_input(self):

        src_data = (255,255,255,255,255,255,44)
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

    def test_006_is_hex(self):

        file_path = '/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt'
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

    def test_007_is_hex(self):

        src_data = (0,0,0,0,0,0,0,0,0,0,44)
        tag1 = gr.tag_t()
        tag1.offset = 0
        tag1.key = pmt.string_to_symbol('spam')
        tag1.value = pmt.from_long(23)
        expected_data = [0] * (int(len(src_data)/2))
        expected_data = [src_data[i] ^ code[i] for i in range(len(expected_data))]
        
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,True,',','packet_len')
        dst = blocks.vector_sink_b()
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
     
        self.tb.run()
        result_data = dst.data()
        result_data = self.combine(result_data)
    
        self.assertEqual(result_data, expected_data)
        
    


if __name__ == '__main__':
    gr_unittest.run(qa_whitening)
