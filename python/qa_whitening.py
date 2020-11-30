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
import lora_sdr_swig as lora_sdr
import pmt
import time

class qa_whitening(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_t(self):
        src_data = "KgOskNhBFeWlkfxA7t3aTUjxgvfMNpXnvCGFdL5IQRRYVeoQxfOeZYC3hFFVUt6f"
        expected_result = "41199311118119151010107121342787237131419821011591592551235810128371477469464161179281515515773688812111154791512771001313151111811714124366504177511041326151612251171315"
        expected_result = False
        whitening = lora_sdr.whitening()
        src = blocks.message_strobe(pmt.intern(src_data), 1000)
        dst_c = blocks.interleaved_char_to_complex()
        dst_t = blocks.vector_sink_c()
        self.lora_sdr_whitening_0 = lora_sdr.whitening()

        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern(src_data), 1000)
        self.tb.msg_connect((self.blocks_message_strobe_0, pmt.string_to_symbol('strobe')), (self.lora_sdr_whitening_0, pmt.string_to_symbol('msg')))

        # self.tb.msg_connect(src,whitening)
        
        self.tb.connect(whitening,dst_c)
        self.tb.connect(dst_c,dst_t)
        # set up fg
        self.tb.start()
        time.sleep(1)
        self.tb.stop()
        self.tb.wait()
        # check data
        result_data = whitening.data()
        print("Result data:")
        print(result_data)
        self.assertEqual(result_data,expected_result)
        print("Test")



if __name__ == '__main__':
    gr_unittest.run(qa_whitening)
