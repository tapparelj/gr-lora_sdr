#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import lora_sdr_python as lora_sdr
import numpy as np

from scipy.special import i0
from utils import *
import lora

SF = 7
N = 2**SF

class qa_partial_ml(gr_unittest.TestCase):
    def setUp (self):
        pass

    def tearDown (self):
        pass

    def _feed_demod(self, stream, tags, id=0, SF=SF):
        tb = gr.top_block()
        partial_ml = lora_sdr.partial_ml(SF, id)
        sink = blocks.vector_sink_f()
        sink_mi1 = blocks.vector_sink_c(N)
        sink_mi2 = blocks.vector_sink_c(N)
        tag_sink = TagSinkInt()
        tagger = Tagger(tags)

        source = blocks.vector_source_c(gr_cast(stream))

        tb.connect(source, tagger)
        tb.connect(tagger, partial_ml)
        tb.connect((partial_ml, 0), sink)
        tb.connect((partial_ml, 0), tag_sink)

        tb.connect((partial_ml, 1), sink_mi1)
        tb.connect((partial_ml, 2), sink_mi2)

        tb.run()
        tags = filter(lambda t: t.key == 'partial_ml', tag_sink.get_tags())
        data = sink.data()
        tb.stop()
        return (data, tags)

    def test_001_single_payload(self):
        print("test_001_single_payload")

        S = 42
        x = lora.gen_sym(SF, S)
        win_tags = {0: ('new_window', {'power1': 1.0, 'power2':0.0, 'win_len':N, 'tau':0.0, 'delta_cfo':0.0,
                        'Tu':SYNC_TYPE_PAYLOAD, 'Ti1':SYNC_TYPE_VOID, 'Ti2':SYNC_TYPE_VOID})}
        y, tags = self._feed_demod(x, win_tags)

        self.assertEqual(len(y), 1)
        self.assertEqual(len(tags), 1)
        demod = tags[0].value

        self.assertEqual(demod['Su'], S)
        self.assertAlmostEqual(demod['Mu'], 1)

        self.assertAlmostEqual(y, i0(1), places=5)

    def test_002_half_payloads(self):
        print("test_002_half_payloads")

        Su, Si1, Si2 = 21, 0, 10
        Pu, Pi = 1.0, 0.5

        x = np.sqrt(Pu)*lora.gen_sym(SF, Su) + np.sqrt(Pi)*np.concatenate([lora.gen_sym(SF, Si1)[N/2:N], lora.gen_sym(SF, Si2)[0:N/2]])
        win_tags = {0: ('new_window', {'power1': Pu, 'power2':Pi, 'win_len':N, 'tau':N/2.0, 'delta_cfo':0.0,
                        'Tu':SYNC_TYPE_PAYLOAD, 'Ti1':SYNC_TYPE_PAYLOAD, 'Ti2':SYNC_TYPE_PAYLOAD})}
        y, tags = self._feed_demod(x, win_tags, id=0)

        self.assertEqual(len(y), 1)
        self.assertEqual(len(tags), 1)
        demod = tags[0].value

        self.assertEqual(demod['Su'], Su)
        self.assertAlmostEqual(demod['Mu'], np.sqrt(Pu), places=5)

        self.assertEqual(demod['Si1'], Si1)
        self.assertAlmostEqual(demod['Mi1'], np.sqrt(Pi)/2, places=4)

        self.assertEqual(demod['Si2'], Si2)
        self.assertAlmostEqual(demod['Mi2'], np.sqrt(Pi)/2, places=4)

        self.assertAlmostEqual(y, i0(Pu) * i0(Pi/2) * i0(Pi/2), places=4)

    def test_003_half_payloads_cfo(self):
        print("test_003_half_payloads_cfo")

        Su, Si1, Si2 = 21, 0, 10
        Pu, Pi = 1.0, 0.5
        delta_cfo = -3.5

        x_u = np.sqrt(Pu)*lora.gen_sym(SF, Su)
        x_i = np.sqrt(Pi)*np.concatenate([lora.gen_sym(SF, Si1)[N/2:N], lora.gen_sym(SF, Si2)[0:N/2]])

        x = x_u + lora.add_cfo(SF, x_i, delta_cfo)
        win_tags = {0: ('new_window', {'power1': Pu, 'power2':Pi, 'win_len':N, 'tau':N/2.0, 'delta_cfo':delta_cfo,
                        'Tu':SYNC_TYPE_PAYLOAD, 'Ti1':SYNC_TYPE_PAYLOAD, 'Ti2':SYNC_TYPE_PAYLOAD})}
        y, tags = self._feed_demod(x, win_tags, id=0)

        self.assertEqual(len(y), 1)
        self.assertEqual(len(tags), 1)
        demod = tags[0].value

        self.assertEqual(demod['Su'], Su)
        self.assertAlmostEqual(demod['Mu'], np.sqrt(Pu), places=2)

        self.assertEqual(demod['Si1'], Si1)
        self.assertAlmostEqual(demod['Mi1'], np.sqrt(Pi)/2, places=2)

        self.assertEqual(demod['Si2'], Si2)
        self.assertAlmostEqual(demod['Mi2'], np.sqrt(Pi)/2, places=2)

        self.assertAlmostEqual(y, i0(Pu) * i0(Pi/2) * i0(Pi/2), places=2)

    def test_004_half_payloads_sto(self):
        print("test_004_half_payloads_sto")

        Su, Si1, Si2 = 21, 20, 110
        Pu, Pi = 1.0, 0.5
        lambda_sto = 0.5
        l_sto = N/2

        ctau = np.ceil(l_sto + lambda_sto)

        x_u = np.sqrt(Pu)*lora.gen_sym(SF, Su)
        x_i = np.sqrt(Pi)*np.concatenate([lora.gen_sym(SF, Si1, sto_frac=lambda_sto)[l_sto:N], lora.gen_sym(SF, Si2, sto_frac=lambda_sto)[0:l_sto]])

        x = x_u + x_i
        win_tags = {0: ('new_window', {'power1': Pu, 'power2':Pi, 'win_len':N, 'tau':(N-l_sto+lambda_sto), 'delta_cfo':0.0,
                        'Tu':SYNC_TYPE_PAYLOAD, 'Ti1':SYNC_TYPE_PAYLOAD, 'Ti2':SYNC_TYPE_PAYLOAD})}
        y, tags = self._feed_demod(x, win_tags, id=0)

        self.assertEqual(len(y), 1)
        self.assertEqual(len(tags), 1)
        demod = tags[0].value

        self.assertEqual(demod['Su'], Su)
        self.assertAlmostEqual(demod['Mu'], np.sqrt(Pu), places=1)

        self.assertEqual(demod['Si1'], Si1)
        self.assertAlmostEqual(demod['Mi1'], np.sqrt(Pi)*(N-ctau)/N, places=1)

        self.assertEqual(demod['Si2'], Si2)
        self.assertAlmostEqual(demod['Mi2'], np.sqrt(Pi)*ctau/N, places=1)


    def test_005_half_payloads_phase(self):
        print("test_005_half_payloads_phase")

        Su, Si1, Si2 = 21, 0, 10
        Pu, Pi = 1.0, 0.5
        theta_u = np.pi/2

        x = np.exp(1j*theta_u)*np.sqrt(Pu)*lora.gen_sym(SF, Su) + np.sqrt(Pi)*np.concatenate([lora.gen_sym(SF, Si1)[N/2:N], lora.gen_sym(SF, Si2)[0:N/2]])
        win_tags = {0: ('new_window', {'power1': Pu, 'power2':Pi, 'win_len':N, 'tau':N/2.0, 'delta_cfo':0.0,
                        'Tu':SYNC_TYPE_PAYLOAD, 'Ti1':SYNC_TYPE_PAYLOAD, 'Ti2':SYNC_TYPE_PAYLOAD})}
        y, tags = self._feed_demod(x, win_tags, id=0)

        self.assertEqual(len(y), 1)
        self.assertEqual(len(tags), 1)
        demod = tags[0].value

        self.assertEqual(demod['Su'], Su)
        self.assertAlmostEqual(demod['Mu'], np.sqrt(Pu), places=2)

        self.assertEqual(demod['Si1'], Si1)
        self.assertAlmostEqual(demod['Mi1'], np.sqrt(Pi)/2, places=4)

        self.assertEqual(demod['Si2'], Si2)
        self.assertAlmostEqual(demod['Mi2'], np.sqrt(Pi)/2, places=4)

        self.assertAlmostEqual(y, i0(Pu) * i0(Pi/2) * i0(Pi/2), places=2)

if __name__ == '__main__':
    gr_unittest.run(qa_partial_ml, "qa_partial_ml.xml")
