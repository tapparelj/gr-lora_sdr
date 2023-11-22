#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                     GNU GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
#
#  Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
#  Everyone is permitted to copy and distribute verbatim copies
#  of this license document, but changing it is not allowed.


from gnuradio import gr, gr_unittest
from gnuradio import analog
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np
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

class qa_tx_buffer(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001_full_buffer_test(self):

        src_data = (0,1,0,0,0,44)
        sf = 7
        samp_rate = 500000
        preamb_len = 8
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        bw = 125000
        SNRdB = -5

        relative_path = "../../data/GRC_default/example_tx_source.txt"
        input_path = os.path.join(script_dir, relative_path) 
        blocks_file_source = blocks.file_source(gr.sizeof_char*1, input_path, False, 0, 0)
        blocks_file_source.set_begin_tag(pmt.PMT_NIL)

        lora_sdr_whitening = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_modulate = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),preamb_len)
        lora_sdr_interleaver = lora_sdr.interleaver(cr, sf, ldro, 125000)
        lora_sdr_header = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc = lora_sdr.add_crc(has_crc)
        blocks_throttle = blocks.throttle(gr.sizeof_gr_complex*1, 1000 ,True)
        blocks_vector_sink = blocks.vector_sink_c(1, 1024)
    
        self.tb.connect((blocks_file_source, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_add_crc, 0), (lora_sdr_hamming_enc, 0))
        self.tb.connect((lora_sdr_gray_demap, 0), (lora_sdr_modulate, 0))
        self.tb.connect((lora_sdr_hamming_enc, 0), (lora_sdr_interleaver, 0))
        self.tb.connect((lora_sdr_header, 0), (lora_sdr_add_crc, 0))
        self.tb.connect((lora_sdr_interleaver, 0), (lora_sdr_gray_demap, 0))
        self.tb.connect((lora_sdr_modulate, 0), (blocks_throttle, 0))
        self.tb.connect((blocks_throttle, 0), (blocks_vector_sink, 0))
        self.tb.connect((lora_sdr_whitening, 0), (lora_sdr_header, 0))
        self.tb.run()

        # Load ref files
        relative_ref_path = "qa_ref/qa_ref_tx/ref_tx_sf7_cr2.bin"
        reference_path = os.path.join(script_dir, relative_ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()
        #print(result_data)

        result_data = blocks_vector_sink.data()
    
        self.assertEqual(result_data, list(ref_data))
        decimalPlace = 7
        # error message in case if test case got failed 
        message = "first and second are not almost equal."
        # assert function() to check if values are almost equal 
        for i in range(len(result_data)):
            self.assertAlmostEqual(result_data[i], ref_data[i], decimalPlace, message) 
    

    def test_002_empty_buffer_before_header_test(self):

        src_data = (0,1,0,0,0,44)
        sf = 7
        samp_rate = 500000
        preamb_len = 8
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        bw = 125000
        SNRdB = -5

        src0 = blocks.vector_source_b(src_data, False, 1, [])
        src1 = blocks.vector_source_c(200 * [1])
        src2 = blocks.vector_source_c(200 * [2])
        relative_path = "../../data/GRC_default/example_tx_source.txt"
        input_path = os.path.join(script_dir, relative_path) 
        blocks_file_source = blocks.file_source(gr.sizeof_char*1, input_path, False, 0, 0)
        blocks_file_source.set_begin_tag(pmt.PMT_NIL)

        lora_sdr_whitening = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_modulate = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),preamb_len)
        lora_sdr_interleaver = lora_sdr.interleaver(cr, sf, ldro, 125000)
        lora_sdr_header = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc = lora_sdr.add_crc(has_crc)
        blocks_throttle = blocks.throttle(gr.sizeof_char*1, 1,True)
        blocks_vector_sink = blocks.vector_sink_c(1, 1024)
    
        self.tb.connect((blocks_file_source, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_add_crc, 0), (lora_sdr_hamming_enc, 0))
        self.tb.connect((lora_sdr_gray_demap, 0), (lora_sdr_modulate, 0))
        self.tb.connect((lora_sdr_hamming_enc, 0), (lora_sdr_interleaver, 0))
        self.tb.connect((lora_sdr_header, 0), (lora_sdr_add_crc, 0))
        self.tb.connect((lora_sdr_interleaver, 0), (lora_sdr_gray_demap, 0))
        self.tb.connect((lora_sdr_modulate, 0), (blocks_vector_sink, 0))
        self.tb.connect((lora_sdr_whitening, 0), (blocks_throttle, 0))
        self.tb.connect((blocks_throttle, 0), (lora_sdr_header, 0))
        self.tb.run()

        # Load ref files
        relative_ref_path = "qa_ref/qa_ref_tx/ref_tx_sf7_cr2.bin"
        reference_path = os.path.join(script_dir, relative_ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()
        #print(result_data)

        result_data = blocks_vector_sink.data()

        decimalPlace = 7
        # error message in case if test case got failed 
        message = "first and second are not almost equal."
        # assert function() to check if values are almost equal 
        for i in range(len(result_data)):
            self.assertAlmostEqual(result_data[i], ref_data[i], decimalPlace, message) 
    
    def test_003_empty_buffer_before_whitening_test(self):

        src_data = (0,1,0,0,0,44)
        sf = 7
        samp_rate = 500000
        preamb_len = 8
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        bw = 125000

        relative_path = "../../data/GRC_default/example_tx_source.txt"
        input_path = os.path.join(script_dir, relative_path) 
        blocks_file_source = blocks.file_source(gr.sizeof_char*1, input_path, False, 0, 0)
        blocks_file_source.set_begin_tag(pmt.PMT_NIL)

        lora_sdr_whitening = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_modulate = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),preamb_len)
        lora_sdr_interleaver = lora_sdr.interleaver(cr, sf, ldro, 125000)
        lora_sdr_header = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc = lora_sdr.add_crc(has_crc)
        blocks_throttle = blocks.throttle(gr.sizeof_char*1, 10,True)
        blocks_vector_sink = blocks.vector_sink_c(1, 1024)
    
        self.tb.connect((blocks_file_source, 0), (blocks_throttle, 0))
        self.tb.connect((lora_sdr_add_crc, 0), (lora_sdr_hamming_enc, 0))
        self.tb.connect((lora_sdr_gray_demap, 0), (lora_sdr_modulate, 0))
        self.tb.connect((lora_sdr_hamming_enc, 0), (lora_sdr_interleaver, 0))
        self.tb.connect((lora_sdr_header, 0), (lora_sdr_add_crc, 0))
        self.tb.connect((lora_sdr_interleaver, 0), (lora_sdr_gray_demap, 0))
        self.tb.connect((lora_sdr_modulate, 0), (blocks_vector_sink, 0))
        self.tb.connect((blocks_throttle, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (lora_sdr_header, 0))
        self.tb.run()

        # Load ref files
        relative_ref_path = "qa_ref/qa_ref_tx/ref_tx_sf7_cr2.bin"
        reference_path = os.path.join(script_dir, relative_ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()
        #print(result_data)

        result_data = blocks_vector_sink.data()

        decimalPlace = 7
        # error message in case if test case got failed 
        message = "first and second are not almost equal."
        # assert function() to check if values are almost equal 
        for i in range(len(result_data)):
            self.assertAlmostEqual(result_data[i], ref_data[i], decimalPlace, message) 
    
      

    

if __name__ == '__main__':
    gr_unittest.run(qa_tx_buffer)

