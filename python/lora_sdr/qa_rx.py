##############################################################################
# File: qa_rx.py
# Date: 21-12-2023
#
# Description: This is a test code for receiver in tx_rx_simulation. 
#              It consists frame_sync, fft_demod, gray_mapping, deinterleaver, 
#              hamming_dec, header_decoder, dewhitening and crc_verify
#
# Function: test_001_functional_test
#   Description: test the general function of receiver (correctness) by input 
#                the output of receiver ref_tx_sf_cr.bin in qa_ref/qa_ref_tx. sf = 7, cr = 2
#                and compare output with reference file 
#                example_tx_source.txt in data/GRC_default folder
##############################################################################


from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np
import time
import os
import sys

try:
    import gnuradio.lora_sdr as lora_sdr
   
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))

script_dir = os.path.dirname(os.path.abspath(__file__))

class qa_rx(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        soft_decoding = False
        sf = 7
        samp_rate = 500000
        preamb_len = 8
        pay_len = 25
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        center_freq = 868.1e6
        bw = 125000

        # initialize the blocks
        lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro, True)
        lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], (int(samp_rate/bw)),preamb_len)
        lora_sdr_fft_demod_0 = lora_sdr.fft_demod(soft_decoding, False)
        lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        lora_sdr_crc_verif_0 = lora_sdr.crc_verif(True, False)
        relative_path = "qa_ref/qa_ref_tx/ref_tx_sf{}_cr{}.bin".format(sf, cr)
        input_file_path = os.path.join(script_dir, relative_path)
        blocks_file_source_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, input_file_path, False, 0, 0)
        blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)
        blocks_vector_sink_x_1 = blocks.vector_sink_b(1, 1024)

        # connect the blocks
        self.tb.msg_connect((lora_sdr_header_decoder_0, 'frame_info'), (lora_sdr_frame_sync_0, 'frame_info'))
        self.tb.connect((blocks_file_source_0_1, 0), (lora_sdr_frame_sync_0, 0))
        self.tb.connect((lora_sdr_deinterleaver_0, 0), (lora_sdr_hamming_dec_0, 0))
        self.tb.connect((lora_sdr_dewhitening_0, 0), (lora_sdr_crc_verif_0, 0))
        self.tb.connect((lora_sdr_fft_demod_0, 0), (lora_sdr_gray_mapping_0, 0))
        self.tb.connect((lora_sdr_frame_sync_0, 0), (lora_sdr_fft_demod_0, 0))
        self.tb.connect((lora_sdr_gray_mapping_0, 0), (lora_sdr_deinterleaver_0, 0))
        self.tb.connect((lora_sdr_hamming_dec_0, 0), (lora_sdr_header_decoder_0, 0))
        self.tb.connect((lora_sdr_header_decoder_0, 0), (lora_sdr_dewhitening_0, 0))
        self.tb.connect((lora_sdr_crc_verif_0, 0), (blocks_vector_sink_x_1, 0))
        self.tb.run()

        # get the output
        result_data = blocks_vector_sink_x_1.data()

        # Load ref files
        ref_input_path = "../../data/GRC_default/example_tx_source.txt"
        ref_path = os.path.join(script_dir, ref_input_path)
        with open(ref_path, "rb") as f3:
            binary_data = f3.read()

        # change the character into integer except the last 44(the comma)
        grouped_data = [binary_data[i:i+1] for i in range(0, len(binary_data)-1, 1)]
        grouped_integers = [int.from_bytes(group, byteorder="big") for group in grouped_data]

        self.assertEqual(grouped_integers, result_data)
    

if __name__ == '__main__':
    gr_unittest.run(qa_rx)
