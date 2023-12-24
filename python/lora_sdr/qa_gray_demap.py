##############################################################################
# File: qa_gray_demap.py
# Date: 21-12-2023
#
# Description: This is a test code for block gray_demapping
#
# Function: test_001_functional_test
#   Description: test the general function of gray demapping
##############################################################################

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
import numpy as np

try:
    import gnuradio.lora_sdr as lora_sdr
   
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))

class qa_gray_demap(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_function_test(self):

        sf = 7
        # set the payload_length
        payload_length = 10
        # the symbol can be seen as integers between 0 and 2^sf - 1
        max_value = 2 ** sf
        # randomly generate the source data
        src_data = np.random.randint(max_value, size=payload_length)

        # initialize the blocks
        lora_sdr_gray_demap = lora_sdr.gray_demap(sf)
        blocks_vector_source = blocks.vector_source_i(src_data, False, 1, [])
        blocks_vector_sink = blocks.vector_sink_i(1, 1024)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_gray_demap, 0))
        self.tb.connect((lora_sdr_gray_demap, 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = blocks_vector_sink.data()

        # generate reference data
        ref_data = [0] * len(src_data)
        for i in range(len(src_data)):
            ref_data[i] = src_data[i]
            for j in range(1, sf):
                ref_data[i]=ref_data[i]^(src_data[i]>>j)
            ref_data[i] = ((ref_data[i]+1) % (1 << sf))

        self.assertEqual(ref_data, result_data)


if __name__ == '__main__':
    gr_unittest.run(qa_gray_demap)
