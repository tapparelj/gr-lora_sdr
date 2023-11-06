from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np

    
f = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx_no_mod/ref_tx_sf7_cr2.bin","r")
# Read the binary data into a NumPy array of complex64
ref_data_mod = np.fromfile(f, dtype=np.int32)

# Convert the complex64 data to complex32

f.close()
f1 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx_no_mod/ref_tx_sf7_cr2_translated.txt", "w")
for i in range(len(ref_data_mod)):
    f1.write(str(ref_data_mod[i]) + ",")
f1.close()

f2 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/temp/ref_tx_with_mod_sf7_cr2.bin","r")
ref_data = np.fromfile(f2, dtype=np.int32)
f2.close()

f3 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/temp/ref_tx_with_mod_sf7_cr2_translated.txt", "w")

for i in range(len(ref_data)):
    f3.write(str(ref_data[i]) + ",")
f3.close()

