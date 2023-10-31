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
import numpy as np

    
f = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_mod/ref_tx_mod_sf7_cr2.bin","r")
# Read the binary data into a NumPy array of complex64
ref_data_mod = np.fromfile(f, dtype=np.complex64)

# Convert the complex64 data to complex32

f.close()
f1 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_mod/ref_tx_mod_sf7_cr2_translated.bin", "wb")
ref_data_mod.tofile(f1)
f1.close()

f2 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx/ref_tx_sf7_cr2.bin","r")
ref_data = np.fromfile(f2, dtype=np.complex64)
f2.close()

f3 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx/ref_tx_sf7_cr2_translated.bin", "wb")
ref_data.tofile(f3)
f3.close()

