from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np

    
# f = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx_no_mod/ref_tx_sf7_cr2.bin","r")
# # Read the binary data into a NumPy array of complex64
# ref_data_mod = np.fromfile(f, dtype=np.int32)

# # Convert the complex64 data to complex32

# f.close()
# f1 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/qa_ref_tx_no_mod/ref_tx_sf7_cr2_translated.txt", "w")
# for i in range(len(ref_data_mod)):
#     f1.write(str(ref_data_mod[i]) + ",")
# f1.close()

# f2 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/temp/add_header6_7_cr2.bin","r")
# ref_data = np.fromfile(f2, dtype=np.int32)
# f2.close()

# f3 = open("/home/yujwu/Documents/gr-lora_sdr/python/lora_sdr/qa_ref/temp/add_header6_sf7_cr2_translated.txt", "w")

# for i in range(len(ref_data)):
#     f3.write(str(ref_data[i]) + ",")
# f3.close()


def build_upchirp(chirp, id, sf, os_factor=4.0):
    N = 2 ** sf
    n_fold = int(N * os_factor - id * os_factor)

    for n in range(int(N * os_factor)):
        if n < n_fold:
            chirp[n] = 1.0 + 0.0j
            chirp[n] *= np.exp(2.0j * np.pi * (n * n / (2 * N) / (os_factor ** 2) + (id / N - 0.5) * n / os_factor))
        else:
            chirp[n] = 1.0 + 0.0j
            chirp[n] *= np.exp(2.0j * np.pi * (n * n / (2 * N) / (os_factor ** 2) + (id / N - 1.5) * n / os_factor))

# Assuming chirp is a NumPy array
chirp = np.zeros(512, dtype=np.complex128)  # Initialize an array of complex numbers

# Call the function with n = 5, sf = 7, and id = 0
build_upchirp(chirp, id=0, sf=7)

# Print the result for chirp[5]
print(chirp[5])

