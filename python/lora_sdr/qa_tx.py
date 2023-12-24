##############################################################################
# File: qa_tx.py
# Date: 21-12-2023
#
# Description: This is a test code for transmitter in tx_rx_simulation. 
#              It consists whitening, add_header, add_crc, hamming_enc, 
#              interleaver, gray demapping, modulate and throttle. If the test fails, 
#              please first check if the reference file is correct. 
#              If it is not, use the ref_tx_generate.py to regenerate
#
# Function: test_001_functional_test
#   Description: test the general function of transmitter (correctness) by input 
#                exampe_tx_source and compare output with reference file 
#                ref_tx_sf_cr.bin in qa_ref/qa_ref_tx folder
#
# Function: test_002_boundary_test
#   Description: test the general function of transmitter (correctness) when 
#               sf is the maximum value and cr is minimum. Input 
#                exampe_tx_source and compare output with reference file 
#                ref_tx_sf_cr.bin in qa_ref/qa_ref_tx folder
##############################################################################

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np
import os
import sys

try:
    import gnuradio.lora_sdr as lora_sdr
    
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))

# get the file path
script_dir = os.path.dirname(os.path.abspath(__file__))

class qa_tx(gr_unittest.TestCase):

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
        bw = 125000

        # initialize the blocks
        lora_sdr_whitening_0 = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),preamb_len)
        lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro, 125000)
        lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        blocks_vector_sink_x_0 = blocks.vector_sink_c(1, 1024)
        blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, (samp_rate*10),True)
        # Define the relative path to the file from the script's directory
        relative_path = "../../data/GRC_default/example_tx_source.txt"
        input_path = os.path.join(script_dir, relative_path)
        blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, input_path, False, 0, 0)
        blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)

        # connect the blocks
        self.tb.connect((blocks_file_source_0_0, 0), (lora_sdr_whitening_0, 0))
        self.tb.connect((blocks_throttle_0, 0), (blocks_vector_sink_x_0, 0))
        self.tb.connect((lora_sdr_add_crc_0, 0), (lora_sdr_hamming_enc_0, 0))
        self.tb.connect((lora_sdr_gray_demap_0, 0), (lora_sdr_modulate_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (lora_sdr_interleaver_0, 0))
        self.tb.connect((lora_sdr_header_0, 0), (lora_sdr_add_crc_0, 0))
        self.tb.connect((lora_sdr_interleaver_0, 0), (lora_sdr_gray_demap_0, 0))
        self.tb.connect((lora_sdr_modulate_0, 0), (blocks_throttle_0, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (lora_sdr_header_0, 0))
        self.tb.run()
        
        # get the output
        result_data = blocks_vector_sink_x_0.data()

        # Load reference files
        ref_path = "qa_ref/qa_ref_tx/ref_tx_sf"+str(sf)+"_cr"+str(cr)+".bin"
        reference_path = os.path.join(script_dir, ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()

        self.assertEqual(result_data, list(ref_data))

    def test_002_boundary_test(self):

        sf = 12
        samp_rate = 500000
        preamb_len = 8
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        bw = 125000

        # initialize the blocks
        lora_sdr_whitening_0 = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),preamb_len)
        lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro, 125000)
        lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        blocks_vector_sink_x_0 = blocks.vector_sink_c(1, 1024)
        blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, (samp_rate*10),True)
        relative_path = "../../data/GRC_default/example_tx_source.txt"
        input_path = os.path.join(script_dir, relative_path)
        blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, input_path, False, 0, 0)
        blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)

        # connect the blocks
        self.tb.connect((blocks_file_source_0_0, 0), (lora_sdr_whitening_0, 0))
        self.tb.connect((blocks_throttle_0, 0), (blocks_vector_sink_x_0, 0))
        self.tb.connect((lora_sdr_add_crc_0, 0), (lora_sdr_hamming_enc_0, 0))
        self.tb.connect((lora_sdr_gray_demap_0, 0), (lora_sdr_modulate_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (lora_sdr_interleaver_0, 0))
        self.tb.connect((lora_sdr_header_0, 0), (lora_sdr_add_crc_0, 0))
        self.tb.connect((lora_sdr_interleaver_0, 0), (lora_sdr_gray_demap_0, 0))
        self.tb.connect((lora_sdr_modulate_0, 0), (blocks_throttle_0, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (lora_sdr_header_0, 0))
        self.tb.run()

        # get the output
        result_data = blocks_vector_sink_x_0.data()

        # Load reference files
        ref_path = "qa_ref/qa_ref_tx/ref_tx_sf"+str(sf)+"_cr"+str(cr)+".bin"
        reference_path = os.path.join(script_dir, ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.complex64)
        f.close()

        self.assertEqual(result_data, list(ref_data))

           
if __name__ == '__main__':
    gr_unittest.run(qa_tx)
