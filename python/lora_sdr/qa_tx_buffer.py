##############################################################################
# File: qa_tx_buffer.py
# Date: 21-12-2023
#
# Description: This is a test code for buffers in transmitter of tx_rx_simulation. 
#              It consists whitening, add_header, add_crc, hamming_enc, 
#              interleaver, gray demapping, modulate and throttle. If the test fails, 
#              please first check if the reference file is correct. 
#              If it is not, use the ref_tx_generate.py to regenerate
#
# Function: test_001_full_test
#   Description: test the buffers of transmitter (correctness) by set slow processing speed(1000) 
#                in throttle at the end of tramsmitter.
#                Input exampe_tx_source and compare output with reference file 
#                ref_tx_sf_cr.bin in qa_ref/qa_ref_tx folder
#
# Function: test_002_empty_buffer_before_header_test
#   Description: test the buffers of transmitter (correctness) by set slow processing 
#                speed(1) in throttle before add_header. In this case, the later
#                blocks would have empty buffer.
#                Input exampe_tx_source and compare output with reference file 
#                ref_tx_sf_cr.bin in qa_ref/qa_ref_tx folder
#
# Function: test_003_empty_buffer_before_whitening_test
#   Description: test the buffers of transmitter (correctness) by set slow processing 
#                speed(1) in throttle before whitening. In this case, the later
#                blocks would have empty buffer.
#                Input exampe_tx_source and compare output with reference file 
#                ref_tx_sf_cr.bin in qa_ref/qa_ref_tx folder
##############################################################################



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

    def test_001_full_buffer_test(self):

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

        # initialize the blocks
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

        # connect the blocks
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

        # get the output
        result_data = blocks_vector_sink.data()

        # Load ref files
        relative_ref_path = "qa_ref/qa_ref_tx/ref_tx_sf7_cr2.bin"
        reference_path = os.path.join(script_dir, relative_ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()

        # error message in case if test case got failed 
        message = "first and second are not almost equal."
        # assertAlmostEqual to check if values are almost equal
        # The decimal place we could tolerate difference is 7
        decimalPlace = 7
        for i in range(len(result_data)):
            self.assertAlmostEqual(result_data[i], ref_data[i], decimalPlace, message) 
    

    def test_002_empty_buffer_before_header_test(self):

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

        # initialize the blocks
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
    
        # connect the blocks
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

        # get the output
        result_data = blocks_vector_sink.data()

        # assertAlmostEqual to check if values are almost equal
        # the decimal place we could tolerate difference is 7
        decimalPlace = 7
        # error message in case if test case got failed 
        message = "first and second are not almost equal."
        # assert function() to check if values are almost equal 
        for i in range(len(result_data)):
            self.assertAlmostEqual(result_data[i], ref_data[i], decimalPlace, message) 
    
    def test_003_empty_buffer_before_whitening_test(self):

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

        # initialize the blocks
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
    
        # connect the blocks
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

        # get the output
        result_data = blocks_vector_sink.data()

        # assertAlmostEqual to check if values are almost equal
        # the decimal place we could tolerate difference is 7
        decimalPlace = 7
        # error message in case if test case got failed 
        message = "first and second are not almost equal."
        # assert function() to check if values are almost equal 
        for i in range(len(result_data)):
            self.assertAlmostEqual(result_data[i], ref_data[i], decimalPlace, message) 
    
      

    

if __name__ == '__main__':
    gr_unittest.run(qa_tx_buffer)

