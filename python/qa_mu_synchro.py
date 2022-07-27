#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 <+YOU OR YOUR COMPANY+>.
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
import lora_sdr_python as lora_sdr
import numpy as np

from utils import *
import lora

SF = 7
N = 2**SF
R = 4
Nsyms = 4


class qa_mu_synchro(gr_unittest.TestCase):
    def setUp (self):
        pass

    def tearDown (self):
        pass

    def _feed_synchro(self, stream, tags, SF=SF, R=R):
        tb = gr.top_block()
        synchronizer = lora_sdr.mu_synchro(SF, R, Nsyms)
        sink = blocks.vector_sink_c()
        tag_sink = TagSink()
        tagger = Tagger(tags)

        source = blocks.vector_source_c(gr_cast(stream))

        tb.connect(source, tagger)
        tb.connect(tagger, synchronizer)
        tb.connect(synchronizer, sink)
        tb.connect(synchronizer, tag_sink)

        tb.run()
        tags = filter(lambda t: t.key == 'new_window', tag_sink.get_tags())
        return (np_cast(sink.data()), tags)

    def check_preamble(self, window_tags, power1=1, power2=0, interf=False, start_offset=0):
        if interf:
            interf_type = SYNC_TYPE_PAYLOAD
        else:
            interf_type = SYNC_TYPE_VOID

        for i, w in enumerate(window_tags[0:12]):
            self.assertEqual(w.offset, start_offset + N * i)
            self.assertEqual(w.value['power1'], power1)
            self.assertEqual(w.value['power2'], power2)
            self.assertEqual(w.value['win_len'], N)
            if (i < 8):
                self.assertEqual(w.value['Tu'], SYNC_TYPE_UPCHIRP)
            elif (i < 10):
                self.assertEqual(w.value['Tu'], SYNC_TYPE_SYNCWORD)
            else:
                self.assertEqual(w.value['Tu'], SYNC_TYPE_DOWNCHIRP)

            self.assertEqual(w.value['Ti1'], interf_type)
            self.assertEqual(w.value['Ti2'], interf_type)

        # Quarter downchirp
        self.assertEqual(window_tags[12].offset, start_offset + N*12)
        self.assertEqual(window_tags[12].value['power1'], power1)
        self.assertEqual(window_tags[12].value['power2'], power2)
        self.assertEqual(window_tags[12].value['win_len'], N/4)
        self.assertEqual(window_tags[12].value['Tu'], SYNC_TYPE_QUARTERDOWN)
        self.assertEqual(window_tags[12].value['Ti1'], interf_type)
        self.assertEqual(window_tags[12].value['Ti2'], interf_type)

     #TODO consider the case where the user 1 frame end before the end of the user two preamble

    def test_001_simple_packet(self):
        print("test_001_simple_packet")

        S = np.arange(Nsyms)
        x = np.concatenate([lora.gen_packet(SF, S, R=R), np.zeros(10*N*R)])

        user_tags = {0: ('new_user', {'power': 1.0, 'sto_int':0, 'sto_frac':0.0, 'cfo_int':0, 'cfo_frac':0.0})}
        y, window_tags = self._feed_synchro(x, user_tags)


        self.assertEqual(len(window_tags), 13 + Nsyms)
        self.check_preamble( window_tags)

        # Payload
        for i, w in enumerate(window_tags[13:13+Nsyms]):
            self.assertEqual(w.offset, N*12 + N/4 + N*i)
            self.assertEqual(w.value['power1'], 1)
            self.assertEqual(w.value['win_len'], N)
            self.assertEqual(w.value['Tu'], SYNC_TYPE_PAYLOAD)
            self.assertEqual(w.value['Ti1'], SYNC_TYPE_VOID)
            self.assertEqual(w.value['Ti2'], SYNC_TYPE_VOID)



    def test_002_two_packets(self):
        print("test_003_two_packets")

        S = np.arange(Nsyms)

        p = lora.gen_packet(SF, S, R=R)
        print(len(p))
        n_z = 6*N*R + 3*N/4*R
        x = np.concatenate([p, np.zeros(n_z), p, np.zeros(10*N*R)])

        i1 = 0
        i2 = len(p) + n_z
        assert i2 % N*R == 0

        user_tags = {}
        user_tags[i1] = ('new_user', {'power': 1.0, 'sto_int':0, 'sto_frac':0.0, 'cfo_int':0, 'cfo_frac':0.0})
        user_tags[i2] = ('new_user', {'power': 1.0, 'sto_int':0, 'sto_frac':0.0, 'cfo_int':0, 'cfo_frac':0.0})

        y, window_tags = self._feed_synchro(x, user_tags)

        self.assertEqual(len(window_tags), (13 + Nsyms) * 2)

        # First user
        self.check_preamble(window_tags, start_offset=0)
        for i, w in enumerate(window_tags[13:13+Nsyms]):
            self.assertEqual(w.offset, N*12 + N/4 + N*i)
            self.assertEqual(w.value['power1'], 1)
            self.assertEqual(w.value['win_len'], N)
            self.assertEqual(w.value['Tu'], SYNC_TYPE_PAYLOAD)
            self.assertEqual(w.value['Ti1'], SYNC_TYPE_VOID)
            self.assertEqual(w.value['Ti2'], SYNC_TYPE_VOID)

        self.assertFloatTuplesAlmostEqual(y[0:len(p)/R], x[0:len(p):R])

        window_tags = window_tags[13+Nsyms:]

        # Second user
        off = len(p)/R
        self.check_preamble(window_tags, start_offset=off)
        for i, w in enumerate(window_tags[13:13+Nsyms]):
            self.assertEqual(w.offset, off + N*12 + N/4 + N*i)
            self.assertEqual(w.value['power1'], 1)
            self.assertEqual(w.value['win_len'], N)
            self.assertEqual(w.value['Tu'], SYNC_TYPE_PAYLOAD)
            self.assertEqual(w.value['Ti1'], SYNC_TYPE_VOID)
            self.assertEqual(w.value['Ti2'], SYNC_TYPE_VOID)

        # for i in range(13):
        #     print(i, "y[{}:{}], x[{}:{}]".format(len(p)+N*i, len(p)+N*i+N, i2+N*i, i2+N*i+N))

        #     a = y[len(p)+N*i : len(p)+N*i+N]
        #     b = x[i2+N*i : i2+N*i+N]
        #     for c,d in zip(a,b):
        #         print(c,d)

        #     self.assertFloatTuplesAlmostEqual(y[len(p)+N*i : len(p)+N*i+N], x[i2+N*i : i2+N*i+N])

        self.assertFloatTuplesAlmostEqual(y[len(p)/R:2*len(p)/R], x[i2:i2+len(p):R], places=5)

if __name__ == '__main__':
    gr_unittest.run(qa_mu_synchro, "qa_mu_synchro.xml")
