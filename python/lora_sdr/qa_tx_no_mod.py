##############################################################################
# File: qa_tx_no_mod.py
# Date: 21-12-2023
#
# Description: This is a test code for transmitter in tx_rx_simulation. 
#              It consists whitening, add_header, add_crc, hamming_enc, 
#              interleaver, gray demapping. If the test fails, 
#              please first check if the reference file is correct. 
#              If it is not, use the ref_tx_no_mod_generate.py to regenerate
#
# Function: test_001_file_source
#    Description: test the general function of transmitter without modulate(correctness) by input 
#                exampe_tx_source and compare output with reference file 
#                ref_tx_sf_cr.bin in qa_ref/qa_ref_tx folder
#
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
    

class qa_tx_no_mod(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_file_source(self):
        # Get the directory of the currently executing script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Define the relative path to the file from the script's directory
        relative_path = "../../data/GRC_default/example_tx_source.txt"

        # Construct the absolute file path
        input_path = os.path.join(script_dir, relative_path)

        sf = 7
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2

        # build up locks   
        lora_sdr_whitening_0 = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro, 125000)       
        lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        blocks_vector_sink_x_0 = blocks.vector_sink_i(1, 1024)       
        blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, input_path, False, 0, 0)
        blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)

        # connect blocks
        self.tb.connect((blocks_file_source_0_0, 0), (lora_sdr_whitening_0, 0))    
        self.tb.connect((lora_sdr_add_crc_0, 0), (lora_sdr_hamming_enc_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (lora_sdr_interleaver_0, 0))
        self.tb.connect((lora_sdr_header_0, 0), (lora_sdr_add_crc_0, 0))
        self.tb.connect((lora_sdr_interleaver_0, 0), (lora_sdr_gray_demap_0, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (lora_sdr_header_0, 0))
        self.tb.connect((lora_sdr_gray_demap_0, 0), (blocks_vector_sink_x_0 , 0))
        self.tb.run()

        # get the output        
        result_data = blocks_vector_sink_x_0.data()

        # Load ref files
        relative_ref_path = "qa_ref/qa_ref_tx_no_mod/ref_tx_sf"+str(sf)+"_cr"+str(cr)+".bin"
        reference_path = os.path.join(script_dir, relative_ref_path)
        f = open(reference_path,"r")
        ref_data = np.fromfile(f, dtype=np.int32)
        f.close()

        self.assertEqual(result_data, list(ref_data))

           
if __name__ == '__main__':
    gr_unittest.run(qa_tx_no_mod)