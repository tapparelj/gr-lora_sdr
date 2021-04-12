#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import lora_sdr_swig as lora_sdr
import numpy as np

from utils import *
import lora

SF = 7
N = 2**SF
R = 8

BUFFER_LEN = (N*14 + N/4)*R

def round_sto(x):
    return np.mod(round(x*R)/R, 1)

def sto_frac_to_int(x):
    return int(round(x*R)/R)

class qa_mu_detection(gr_unittest.TestCase):
    def setUp (self):
        # self.tb = gr.top_block()
        pass

    def tearDown (self):
        # self.tb = None
        pass
        
    def _feed_detector(self, stream, SF=SF, R=R):
        tb = gr.top_block()
        detector = lora_sdr.mu_detection(SF, R,-9)
        
        sink = blocks.vector_sink_c()
        tag_sink = TagSink()

        source = blocks.vector_source_c(gr_cast(stream))

        tb.connect(source, detector)
        tb.connect(detector, sink)
        tb.connect(detector, tag_sink)

        tb.run()
        detects = filter(lambda t: t.key == 'new_user', tag_sink.get_tags())
        return (np_cast(sink.data()), detects)

    def test_001_nothing(self):
        print("test_001_nothing")
        x = np.zeros(N * R * 14)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 0)

    def test_002_simple_preamble(self):
        print("test_002_simple_preamble")
        x = np.concatenate([lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertFloatTuplesAlmostEqual(x[0:N], y[BUFFER_LEN:BUFFER_LEN + N])
        self.assertEqual(d.offset, BUFFER_LEN)
        self.assertEqual(d.value['sto_int'], (BUFFER_LEN/R) % N)
        self.assertEqual(d.value['cfo_int'], 0)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], 0)
        self.assertAlmostEqual(d.value['power'], 1, places=6)

    def test_003_simple_payload(self):
        print("test_003_simple_payload")
        S = [0, 42] * 10
        x = lora.gen_syms(SF, S, R=R, sto_frac=0.1)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 0)

    def test_010_sto_int_intrasym(self):
        print("test_010_sto_int_intrasym")

        M = 5
        x = np.concatenate([np.zeros(M*R), lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        k = BUFFER_LEN + M*R
        self.assertEqual(d.offset, k)
        self.assertEqual(d.value['sto_int'], (k/R) % N)
        self.assertEqual(d.value['cfo_int'], 0)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], 0)

    def test_011_sto_int_intersym(self):
        print("test_011_sto_int_intersym")

        M = 85
        x = np.concatenate([np.zeros((N+M)*R), lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        k = BUFFER_LEN + (N + M)*R
        self.assertEqual(d.value['sto_int'], (k/R) % N)
        self.assertEqual(d.value['cfo_int'], 0)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], 0)

    def test_012_sto_frac_low(self):
        print("test_012_sto_frac_low")

        sto_frac = 0.33
        x = np.concatenate([[0]*int(sto_frac * R), lora.gen_preamble(SF, R=R, sto_frac=np.mod(sto_frac, 1.0/R)), np.zeros(3*N*R)])
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertAlmostEqual(d.value['sto_frac'], round_sto(sto_frac))
        self.assertAlmostEqual(d.value['cfo_frac'], 0)

    def test_013_sto_frac_high(self):
        print("test_013_sto_frac_high")

        sto_frac = 0.68
        x = np.concatenate([[0]*int(sto_frac * R), lora.gen_preamble(SF, R=R, sto_frac=np.mod(sto_frac, 1.0/R)), np.zeros(3*N*R)])
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertAlmostEqual(d.value['sto_frac'], round_sto(sto_frac))
        self.assertAlmostEqual(d.value['cfo_frac'], 0)

    def test_014_cfo_int(self):
        print("test_014_cfo_int")

        L_CFO = 30.0

        x = np.concatenate([lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])

        x = lora.add_cfo(SF, x, L_CFO, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        k = BUFFER_LEN
        self.assertEqual(d.offset, k)
        self.assertEqual(d.value['sto_int'], (k/R) % N)
        self.assertEqual(d.value['cfo_int'], L_CFO)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], 0, places=5)

    def test_015_sto_cfo_int(self):
        print("test_015_sto_cfo_int")

        L_STO = 84
        L_CFO = -20
        x = np.concatenate([np.zeros((L_STO)*R), lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        x = lora.add_cfo(SF, x, L_CFO, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        k = BUFFER_LEN + L_STO*R
        self.assertEqual(d.offset, k)
        self.assertEqual(d.value['sto_int'], (k/R) % N)
        self.assertEqual(d.value['cfo_int'], L_CFO)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], 0, places = 5)


    def test_020_cfo_frac(self):
        print("test_020_cfo_frac")
        phi = 0.4
        x = np.concatenate([lora.gen_preamble(SF,R=R), np.zeros(3*N*R)])
        x = lora.add_cfo(SF, x, phi, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertEqual(d.value['sto_int'], (BUFFER_LEN/R) % N)
        self.assertEqual(d.value['cfo_int'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], phi, places=5)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['power'], 1, places=6)

    def test_021_cfo_int(self):
        print("test_021_cfo_int")
        phi = 5.0
        x = np.concatenate([lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        x = lora.add_cfo(SF, x, phi, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertEqual(d.value['sto_int'], (BUFFER_LEN/R) % N)
        self.assertEqual(d.value['cfo_int'], 5)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], 0.0, places=5)
        self.assertAlmostEqual(d.value['power'], 1, places=6)

    def test_022_cfo_int_frac(self):
        print("test_022_cfo_int_frac")
        phi = -3.42
        x = np.concatenate([lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        x = lora.add_cfo(SF, x, phi, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertEqual(d.value['sto_int'], (BUFFER_LEN/R) % N)
        self.assertEqual(d.value['cfo_int'], -3)
        self.assertAlmostEqual(d.value['sto_frac'], 0)
        self.assertAlmostEqual(d.value['cfo_frac'], -0.42, places=2)
        self.assertAlmostEqual(d.value['power'], 1, places=1)

    def _test_cfo_sto(self, CFO, STO):
        CFO_int = np.round(CFO).astype(int)
        CFO_frac = CFO - CFO_int
        STO_int = np.floor(STO).astype(int)
        STO_frac = STO - STO_int

        x = np.concatenate([np.zeros(STO_int*R + int(STO_frac * R)), lora.gen_preamble(SF, R=R, sto_frac=np.mod(STO_frac, 1.0/R)), np.zeros(3*N*R)])
        x = lora.add_cfo(SF, x, CFO, R = R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        residual_int = ((d.value['sto_int'] + d.value['cfo_int']) - (STO_int + CFO_int) - N/4) % N
        self.assertIn(residual_int, (N-1, 0, 1))
        self.assertAlmostEqual(d.value['cfo_frac'], CFO_frac, places=3)
        self.assertAlmostEqual(d.value['sto_frac'], round_sto(STO_frac))

    def test_030_cfo_sto(self):
        print("test_030_cfo_sto")
        self._test_cfo_sto(-3.0, 10.00)

    def test_031_cfo_sto(self):
        print("test_031_cfo_sto")

        self._test_cfo_sto(10.40, 121.30)

    def test_032_cfo_sto(self):
        print("test_032_cfo_sto")
        self._test_cfo_sto(-0.25, 42.25)

    # def test_033_cfo_sto(self):
    #     print("test_033_cfo_sto")
    #     for i in np.arange(1.6,10,0.2):
    #
    #         for j in np.arange(0,2**SF,0.2):
    #             print "cfo=",i," sto= ",j
    #             self._test_cfo_sto(i, j)
    #         # print "cfo= ",i


    def test_040_unit_power(self):
        print("test_040_unit_power")

        phi = 0.3
        P = 1
        x = np.concatenate([lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        x = lora.add_cfo(SF, x, phi, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertEqual(d.offset, BUFFER_LEN)
        self.assertAlmostEqual(d.value['cfo_frac'], phi)
        self.assertAlmostEqual(d.value['power'], P, places=6)

    def test_041_small_power(self):
        print("test_041_small_power")

        P_dB = -1
        phi = 0.3

        P = 10**(P_dB/10.0)
        x = np.concatenate([lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        x = np.sqrt(P) * lora.add_cfo(SF, x, phi, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertEqual(d.offset, BUFFER_LEN)
        self.assertAlmostEqual(d.value['cfo_frac'], phi)
        self.assertAlmostEqual(d.value['power'], P, places=4)

    def test_042_strong_power(self):
        print("test_042_strong_power")

        P_dB = 3
        phi = 0.3

        P = 10**(P_dB/10.0)
        x = np.concatenate([lora.gen_preamble(SF, R=R), np.zeros(3*N*R)])
        x = np.sqrt(P) * lora.add_cfo(SF, x, phi, R=R)
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        self.assertEqual(d.offset, BUFFER_LEN)
        self.assertAlmostEqual(d.value['cfo_frac'], phi)
        self.assertAlmostEqual(d.value['power'], P, places=4)

    def test_043_strong_source(self):
        print("test_043_strong_source")

        P_dB = 9
        phi = 0.3

        P = 10**(P_dB/10.0)
        n = np.tile(np.arange(0, N * R), 14)
        x = np.exp(1j*2*np.pi*n/(N*R))
        x = np.sqrt(P) * lora.add_cfo(SF, x, phi, R=R)

        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 0)

    def test_050_weak_interferer(self):
        print("test_050_weak_interferer")

        Pi_dB = -3
        phi_u = 6.6
        sto_frac_u = 0.49
        sto_int_u = 48

        S = [0, 64, 32, 96, 0, 64, 24, 100] * 4
        x_i = lora.gen_syms(SF, S, R=R)[:int(N*R*15.25)]
        n_pad = sto_int_u*R + int(sto_frac_u * R)
        x_u = np.concatenate([ np.zeros(n_pad), 
                               lora.gen_preamble(SF, R=R, sto_frac=np.mod(sto_frac_u, 1.0/R)), 
                               np.zeros(3*N*R - n_pad)
                            ])

        P_i = 10**(Pi_dB/10.0)
        x = lora.add_cfo(SF, x_u, phi_u, R=R) + np.sqrt(P_i) * x_i
        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]

        cfo_int = np.round(phi_u).astype(int)
        residual_int = ((d.value['sto_int'] + d.value['cfo_int']) - (sto_int_u + cfo_int) - N/4) % N
        self.assertIn(residual_int, (N-1, 0, 1))
        self.assertAlmostEqual(d.value['cfo_frac'], phi_u - cfo_int, places=1)
        self.assertAlmostEqual(d.value['sto_frac'], round_sto(sto_frac_u))

    # def test_051_strong_interferer(self):
    #     print("test_051_strong_interferer")

    #     Pi_dB = 4
    #     phi_u = -2.4
    #     sto_frac_u = 0.72
    #     sto_int_u = 127

    #     S = [0, 42] * 16
    #     x_i = lora.gen_syms(SF, S, R=R)[:int(N*R*15.25)]
    #     n_pad = sto_int_u*R + int(sto_frac_u * R)
    #     x_u = np.concatenate([ np.zeros(n_pad), 
    #                            lora.gen_preamble(SF, R=R, sto_frac=np.mod(sto_frac_u, 1.0/R)), 
    #                            np.zeros(3*N*R - n_pad)
    #                         ])

    #     P_i = 10**(Pi_dB/10.0)
    #     x = lora.add_cfo(SF, x_u, phi_u, R=R) + np.sqrt(P_i) * x_i
    #     y, detects = self._feed_detector(x)

    #     self.assertEqual(len(detects), 1)
    #     d = detects[0]

    #     cfo_int = np.round(phi_u).astype(int)
    #     residual_int = ((d.value['sto_int'] + d.value['cfo_int']) - (sto_int_u + cfo_int) - N/4) % N
    #     self.assertIn(residual_int, (N-1, 0, 1))
    #     self.assertAlmostEqual(d.value['cfo_frac'], phi_u - cfo_int, places=1)
    #     self.assertAlmostEqual(d.value['sto_frac'], round_sto(sto_frac_u))

    def test_052_full_packet(self):
        S = [0, 64, 32, 96, 0, 64, 24, 100] * 4
        x = np.concatenate([lora.gen_packet(SF, S, R=R), np.zeros(15*N*R)])

        y, detects = self._feed_detector(x)

        self.assertEqual(len(detects), 1)
        d = detects[0]
        self.assertEqual(d.offset, BUFFER_LEN)
        
if __name__ == '__main__':
    gr_unittest.run(qa_mu_detection, "qa_mu_detection.xml")
