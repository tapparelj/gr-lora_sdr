#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright some guys
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
import pmt
from foo import periodic_msg_source
import time
from gnuradio import gr, gr_unittest
from gnuradio import blocks
import jitc_swig as jitc
#from foo import periodic_msg_source

class qa_random_sequenced_pdu (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        ##################################################
        # Blocks
        ##################################################
        self.jitc_random_sequenced_pdu_0 = jitc.random_sequenced_pdu(4, 4, 0xFF, 2, 0)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("TEST"), 1000)
        self.blocks_message_debug_0 = blocks.message_debug()

        ##################################################
        # Connections
        ##################################################
        self.tb.msg_connect((self.blocks_message_strobe_0, pmt.string_to_symbol('strobe')), (self.jitc_random_sequenced_pdu_0, pmt.string_to_symbol('generate')))
        self.tb.msg_connect((self.jitc_random_sequenced_pdu_0, 'pdus'), (self.blocks_message_debug_0, 'print_pdu'))

        # need to let the test run for a short time and then stop
        self.tb.start()
        time.sleep(1)
        self.tb.stop()
        self.tb.wait()

if __name__ == '__main__':
    gr_unittest.run(qa_random_sequenced_pdu, "qa_random_sequenced_pdu.xml")