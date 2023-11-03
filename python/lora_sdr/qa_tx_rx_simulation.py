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


# from gnuradio import blocks
try:
    import gnuradio.lora_sdr as lora_sdr
    # from gnuradio.lora_sdr import whitening
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    from gnuradio.lora_sdr import whitening

class qa_tx_rx_simulation(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    # def test_instance(self):
    #     # FIXME: Test will fail until you pass sensible arguments to the constructor
    #     instance = whitening()

    def test_001(self):

        src_data = (0,1,1,0,0,0,0,0,0,0,44)
        samp_rate = 500000
        bw = 125000
        sf = 7
        cr = 2
        clk_offset = 0
        SNRdB = -5
        pay_len = 16
        ldro = False
        impl_head = False
        preamb_len = 8
        has_crc = True
        soft_decoding = False
        center_freq = 868.1e6
        # expected_data = [0] * (len(src_data) - 1)
        
        # for i in range(len(src_data)-1):
        #     expected_data[i] = (src_data[i]^code[i])
        #     print(hex(expected_data[i]))

        # build up blocks
        lora_sdr_whitening_0 = lora_sdr.whitening(False,False,',','packet_len')
        lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [0x12], (int(20*2**sf*samp_rate/bw)),preamb_len)
        lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, ldro, 125000)
        lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro, True)
        lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], (int(samp_rate/bw)),preamb_len)
        lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, False)
        lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        lora_sdr_crc_verif_0 = lora_sdr.crc_verif( True, False)
        lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        # self.channels_channel_model_0 = channels.channel_model(
        #     noise_voltage=(10**(-SNRdB/20)),
        #     frequency_offset=(center_freq*clk_offset*1e-6/samp_rate),
        #     epsilon=(1.0+clk_offset*1e-6),
        #     taps=[1.0 + 0.0j],
        #     noise_seed=0,
        #     block_tags=True)
        # self.channels_channel_model_0.set_min_output_buffer((int(2**sf*samp_rate/bw*1.1)))
        blocks_vector_source_x_0 = blocks.vector_source_b(src_data, False, 1, [])
        blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, (samp_rate*10),True)
        blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, '/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt', False, 0, 0)
        blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)

        # connect blocks
        self.tb.msg_connect((lora_sdr_header_decoder_0, 'frame_info'), (lora_sdr_frame_sync_0, 'frame_info'))
        self.tb.connect((blocks_vector_source_x_0, 0), (lora_sdr_whitening_0, 0))
        self.tb.connect((blocks_throttle_0, 0), (lora_sdr_frame_sync_0, 0))
        self.tb.connect((lora_sdr_add_crc_0, 0), (lora_sdr_hamming_enc_0, 0))
        self.tb.connect((lora_sdr_deinterleaver_0, 0), (lora_sdr_hamming_dec_0, 0))
        self.tb.connect((lora_sdr_dewhitening_0, 0), (lora_sdr_crc_verif_0, 0))
        self.tb.connect((lora_sdr_fft_demod_0, 0), (lora_sdr_gray_mapping_0, 0))
        self.tb.connect((lora_sdr_frame_sync_0, 0), (lora_sdr_fft_demod_0, 0))
        self.tb.connect((lora_sdr_gray_demap_0, 0), (lora_sdr_modulate_0, 0))
        self.tb.connect((lora_sdr_gray_mapping_0, 0), (lora_sdr_deinterleaver_0, 0))
        self.tb.connect((lora_sdr_hamming_dec_0, 0), (lora_sdr_header_decoder_0, 0))
        self.tb.connect((lora_sdr_hamming_enc_0, 0), (lora_sdr_interleaver_0, 0))
        self.tb.connect((lora_sdr_header_0, 0), (lora_sdr_add_crc_0, 0))
        self.tb.connect((lora_sdr_header_decoder_0, 0), (lora_sdr_dewhitening_0, 0))
        self.tb.connect((lora_sdr_interleaver_0, 0), (lora_sdr_gray_demap_0, 0))
        self.tb.connect((lora_sdr_modulate_0, 0), (blocks_throttle_0, 0))
        self.tb.connect((lora_sdr_whitening_0, 0), (lora_sdr_header_0, 0))
 
        # compare results
        self.tb.run()
        
if __name__ == '__main__':
    gr_unittest.run(qa_tx_rx_simulation)
