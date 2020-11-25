#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 "Martyn van Dijke".
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import pmt
import lora_sdr_swig as lora_sdr
from gnuradio import filter


class qa_lora_sdr(gr_unittest.TestCase):
    """Main class of unit test cases for the entire lora sdr

    Args:
        gr_unittest ([type]): [description]
    """

    def setUp(self):
        """Setup for testing
        """
        #Setup variables
        self.tb = gr.top_block()
        self.bw = bw = 250000
        self.sf = sf = 7
        self.samp_rate = samp_rate = bw
        self.pay_len = pay_len = 64
        self.n_frame = n_frame = 8
        self.mult_const = mult_const = 1
        self.impl_head = impl_head = True
        self.has_crc = has_crc = False
        self.frame_period = frame_period = 200
        self.cr = cr = 0

        #Setup blocks
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=4,
                decimation=1,
                taps=None,
                fractional_bw=None)
        self.lora_sdr_whitening_0 = lora_sdr.whitening()
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw)
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf)
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc)
        self.lora_sdr_header_0 = lora_sdr.header(impl_head, has_crc, cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_gray_decode_0 = lora_sdr.gray_decode(sf)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(samp_rate, bw, sf, impl_head)
        self.lora_sdr_err_measures_0 = lora_sdr.err_measures()
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_data_source_0_1_0 = lora_sdr.data_source(pay_len, n_frame)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif()
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(has_crc)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_message_strobe_random_0_1_0 = blocks.message_strobe_random(pmt.intern(''), blocks.STROBE_UNIFORM, frame_period, 5)

        #Setup Connections
        self.tb.msg_connect((self.blocks_message_strobe_random_0_1_0, 'strobe'), (self.lora_sdr_data_source_0_1_0, 'trigg'))
        self.tb.msg_connect((self.lora_sdr_crc_verif_0, 'msg'), (self.lora_sdr_err_measures_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_add_crc_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_err_measures_0, 'ref'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_header_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_interleaver_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_modulate_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_data_source_0_1_0, 'msg'), (self.lora_sdr_whitening_0, 'msg'))
        self.tb.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_deinterleaver_0, 'new_frame'))
        self.tb.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_dewhitening_0, 'new_frame'))
        self.tb.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_fft_demod_0, 'new_frame'))
        self.tb.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_hamming_dec_0, 'new_frame'))
        self.tb.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_header_decoder_0, 'new_frame'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'pay_len'), (self.lora_sdr_crc_verif_0, 'pay_len'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_deinterleaver_0, 'CR'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'pay_len'), (self.lora_sdr_dewhitening_0, 'pay_len'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'pay_len'), (self.lora_sdr_frame_sync_0, 'pay_len'))
        self.tb.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.tb.connect((self.blocks_throttle_0, 0), (self.rational_resampler_xxx_0, 0))
        self.tb.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.tb.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.tb.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.tb.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_enc_0, 0))
        self.tb.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.tb.connect((self.lora_sdr_gray_decode_0, 0), (self.lora_sdr_modulate_0, 0))
        self.tb.connect((self.lora_sdr_gray_enc_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.tb.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.tb.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.tb.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.tb.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))

    def tearDown(self):
        self.tb = None

    def test_001_t(self):
        """[summary]
        """
        # set up fg
        self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_lora_sdr)
