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
from mu_demod import mu_demod

from scipy.special import i0
from utils import *
import lora

SF = 7
N = 2**SF
Ki = N
Ku = 1
R = 8


class qa_mu_demod(gr_unittest.TestCase):
    def setUp (self):
        pass

    def tearDown (self):
        pass

    def _feed_system(self, stream, SF=SF, R=1, Nsyms=1):
        tb = gr.top_block()

        detector = lora_sdr.mu_detection( SF, R,-14)
        synchronizer = lora_sdr.mu_synchro(SF, R, Nsyms)
        demod = mu_demod(SF, Ku)

        sink_u1 = blocks.vector_sink_s()
        sink_u2 = blocks.vector_sink_s()
        sink_snr = blocks.vector_sink_f()

        source = blocks.vector_source_c(gr_cast(stream))

        tb.connect(source, detector)
        tb.connect(detector, synchronizer)
        tb.connect(synchronizer, demod)
        tb.connect((demod, 0), sink_u1)
        tb.connect((demod, 1), sink_u2)
        tb.connect((demod, 2), sink_snr)

        tb.run()
        S1 = sink_u1.data()
        S2 = sink_u2.data()
        tb.stop()
        tb = None
        return (S1, S2)

    def test_001_system_su(self):
        print("test_001_system_su")

        R = 8
        S1 = (0, 10, 20, 30, 40, 50, 60, 70)

        x = np.concatenate([lora.gen_packet(SF, S1, R=R), np.zeros(15*N*R)])
        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))

        self.assertEqual(S1, S1_out)
        self.assertEqual(len(S2_out), 0)

    def test_002_system_su_cfo(self):
        print("test_002_system_su_cfo")

        R = 8
        S1 = (0, 10, 20, 30, 40, 50, 60, 70, 80)
        cfo = 10.5 # Should trigger an integer offset of 1 in the detection bock


        x = np.concatenate([lora.gen_packet(SF, S1, R=R), np.zeros(15*N*R)])
        x = lora.add_cfo(SF, x, cfo, R=R)
        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))

        self.assertEqual(S1, S1_out)
        self.assertEqual(len(S2_out), 0)

    def test_003_system_su_sto(self):
        print("test_003_system_su_sto")

        R = 8
        S1 = (0, 10, 20, 30, 40, 50, 60, 70, 80)

        tau = 30.5
        tau_samples = int(round(tau*R))

        x = np.concatenate([np.zeros(tau_samples), lora.gen_packet(SF, S1, R=R), np.zeros(15*N*R)])
        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))

        self.assertEqual(S1, S1_out)
        self.assertEqual(len(S2_out), 0)

    def test_004_system_su_powers(self):
        print("test_004_system_su_powers")

        R = 8
        S1 = (0, 10, 20, 30, 40, 50, 60, 70, 80)

        theta_u = np.pi/4
        P1 = [0, 1, 2, 3, 4, 6, 20] # TODO more powers

        for P in P1:
            P_lin = 10**(P/10.0)
            x = np.sqrt(P_lin) * np.exp(1j*theta_u) * np.concatenate([lora.gen_packet(SF, S1, R=R), np.zeros(15*N*R)])
            S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
            self.assertEqual(S1, S1_out)
            self.assertEqual(len(S2_out), 0)

            theta_u += np.pi/4

    def test_005_system_su_twice(self):
        print("test_005_system_su_twice")

        R = 8
        S1 = (0, 10, 20, 30, 40, 50, 60, 70, 80)

        p = lora.gen_packet(SF, S1, R=R)
        n_z = 6*N*R + 3*N/4*R
        x = np.concatenate([p, np.zeros(n_z), p, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))

        self.assertEqual(S1 * 2, S1_out)
        self.assertEqual(len(S2_out), 0)

    def test_010_system_mu_sync(self):
        print("test_010_system_mu_sync")

        P1_dB = 0
        P2_dB = 3
        R = 8

        tau = int(14.0*R*N)


        R = 8
        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 2
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 2

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2])

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)

    def test_011_system_mu_STOint_quarter_overlap(self):
        print("test_011_system_mu_STOint_quarter_overlap")
        self.maxDiff = None
        P1_dB = -10 #too high power leads to false detection
        P2_dB = -7
        R = 8

        tau = int(15*R*N + 17*R)

        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 3
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 3

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2])

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)
    
    def test_012_system_mu_STOint_quarter_inside(self):
        print("test_012_system_mu_STOint_quarter_inside")
        self.maxDiff = None
        P1_dB = -10 #too high power leads to false detection
        P2_dB = -7
        R = 8

        tau = int(15*R*N + 56*R)

        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 3
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 3

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2])

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)

    def test_013_system_mu_STOint_0(self):
        print("test_013_system_mu_STOint_0")
        self.maxDiff = None
        P1_dB = -10 #too high power leads to false detection
        P2_dB = -7
        R = 8

        tau = int(15*R*N + 0*R)

        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 3
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 3

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2])

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)

    def test_014_system_mu_STOint_32(self):
        print("test_014_system_mu_STOint_32")
        self.maxDiff = None
        P1_dB = -10 #too high power leads to false detection
        P2_dB = -7
        R = 8

        tau = int(15*R*N + 96*R)

        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 3
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 3

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2])

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)
    

    def test_015_system_mu_STOfrac_quarter_inside(self): #very unstable can work or not between tw0 consecutive executions
        print("test_015_system_mu_STOfrac_quarter_inside")
        self.maxDiff = None
        P1_dB = -10 #too high power leads to false detection
        P2_dB = -7
        R = 8

        tau = int(15*R*N + 32*R+1)

        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 3
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 3

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([np.zeros(0),p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2,np.zeros(0)])

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)

    def test_016_system_mu_STOfrac_quarter_overlap(self):
        print("test_016_system_mu_STOfrac_quarter_overlap")
        self.maxDiff = None
        P1_dB = -10 #too high power leads to false detection
        P2_dB = -7
        R = 8

        tau = int(15*R*N + 17*R+3)

        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 3
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 3

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([np.zeros(6),p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2,np.zeros(6)])

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)

    def system_mu(self, STO, CFO):
        print "test_system_mu ", STO, CFO 
        self.maxDiff = None
        P1_dB = -12 #too high power leads to false detection
        P2_dB = -9


        tau = int(15*R*N + STO*R)

        S1 = (5, 10, 20, 30, 40, 50, 60, 70) * 3
        S2 = (42, 101, 89, 15, 127, 0, 74, 94) * 3

        p1 = lora.gen_packet(SF, S1, R=R)
        p2 = lora.gen_packet(SF, S2, R=R)

        x1 = np.sqrt(10**(P1_dB/10.0)) * np.concatenate([np.zeros(0),p1, np.zeros(tau)])
        x2 = np.sqrt(10**(P2_dB/10.0)) * np.concatenate([np.zeros(tau), p2,np.zeros(0)])

        x2 = lora.add_cfo(SF, x2, CFO, R=R)

        x = np.concatenate([x1 + x2, np.zeros(20*N*R)])
        

        S1_out, S2_out = self._feed_system(x, R=R, Nsyms=len(S1))
        self.assertEqual(S1, S1_out)
        self.assertEqual(S2, S2_out)

   
if __name__ == '__main__':
    #import os
    #print 'Blocked waiting for GDB attach (pid = %d)' % (os.getpid(),)
    #raw_input ('Press Enter to continue: ')
    gr_unittest.run(qa_mu_demod, "qa_mu_demod.xml")
