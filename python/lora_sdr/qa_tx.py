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
from table import code
import pmt
import numpy as np


# from gnuradio import blocks
try:
    import gnuradio.lora_sdr as lora_sdr
    
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    

class qa_tx(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001(self):

        soft_decoding = soft_decoding = False
        src_data = (0,1,1,0,0,0,0,0,0,0,44)
        sf = 7
        samp_rate = 500000
        preamb_len = 8
        pay_len = 16
        ldro = False
        impl_head = False
        has_crc = True
        cr = 2
        clk_offset = 0
        center_freq = 868.1e6
        bw = 125000
        SNRdB = -5

        # build up locks   
        lora_sdr_whitening_0 = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro, 125000)       
        lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        blocks_vector_sink_x_0 = blocks.vector_sink_i(1, 1024)       
        blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, "/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt", False, 0, 0)
        blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)
        blocks_file_sink_0 = blocks.file_sink(gr.sizeof_int*1, '/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/tx_test_result_data_cr2_sf7', False)
        blocks_file_sink_0.set_unbuffered(False)

        # connect blocks
        #self.tb.connect((blocks_vector_source_x_0, 0), (lora_sdr_whitening_0, 0))
        self.tb.connect((blocks_file_source_0_0, 0), (lora_sdr_whitening_0, 0))    
        self.tb.connect((lora_sdr_add_crc_0, 0), (lora_sdr_hamming_enc_0, 0))
        #self.tb.connect((lora_sdr_gray_demap_0, 0), (blocks_file_sink_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (lora_sdr_interleaver_0, 0))
        self.tb.connect((lora_sdr_header_0, 0), (lora_sdr_add_crc_0, 0))
        self.tb.connect((lora_sdr_interleaver_0, 0), (lora_sdr_gray_demap_0, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (lora_sdr_header_0, 0))
        self.tb.connect((lora_sdr_gray_demap_0, 0), (blocks_vector_sink_x_0 , 0))
        self.tb.run()
        result_data = blocks_vector_sink_x_0.data()
        # Load ref files
        f = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx_no_mod/ref_tx_sf"+str(sf)+"_cr"+str(cr)+".bin","r")
        ref_data = np.fromfile(f, dtype=np.int32)
        f.close()

        self.assertEqual(result_data, list(ref_data))
        # # write results in file 
        # f = open("test_sf"+str(sf)+"_"+"cr"+str(cr)+".txt","wb")
        # for i in range(len(result_data)):
        #     # print(result_data[i])
        #     f.write(str(result_data[i]) + ",")
           
if __name__ == '__main__':
    gr_unittest.run(qa_tx)
