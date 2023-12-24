##############################################################################
# File: qa_gray_mapping.py
# Date: 21-12-2023
#
# Description: This is a test code for block gray_mapping, here we only consider hardcoding
#
# Function: make_tag
#   Description: Create a GNU Radio tag with specified key, value, offset, and optional source ID.
#   Input: key (str) - Key for the tag, value - Value for the tag, 
#          offset (int) - Offset of the tag in intput data, srcid (optional) - Source ID for the tag, default is None
#   Output: gr.tag_t - GNU Radio tag object with specified attributes
#
# Function: hamming_encode
#   Description: Encode a sequence of source data using Hamming coding.
#                The function adds parity bits to the data 
#   Input: sf (int) - Spreading factor, cr (int) - Coding rate, src_data (list) 
#   Output: list - Encoded data with added parity bits
#
# Function: test_001_function_test
#    Description: test the general function of gray_mapping
#
##############################################################################


from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np


# from gnuradio import blocks
try:
    import gnuradio.lora_sdr as lora_sdr
   
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))

def make_tag(key, value, offset, srcid=None):
    tag = gr.tag_t()
    tag.key = pmt.string_to_symbol(key)
    tag.value = value
    tag.offset = offset
    if srcid is not None:
        tag.srcid = pmt.to_pmt(srcid)
    return tag

def gray_mapping(src_data):

    ref_data = [0] * len(src_data)
    for i in range(len(src_data)):
        ref_data[i] = src_data[i] ^ (src_data[i] >> 1)
    return ref_data

class qa_gray_mapping(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        sf = 7
        # set the payload length randomly
        payload_length = 20
        # symbol can be seen as integer between 0 and 2^sf - 1
        max_value = 2**sf
        # randomly generate the nibbles output by whitening block
        src_data = np.random.randint(max_value, size=payload_length)
        soft_decoding = False 

        # generate dictionary for is_header and sf
        a = pmt.make_dict()
        key1 = pmt.intern("is_header")
        is_header = pmt.from_bool(False)
        key2 = pmt.intern("sf")
        sf_tag = pmt.from_long(sf)
        a = pmt.dict_add(a, key1, is_header)
        a = pmt.dict_add(a, key2, sf_tag)

        # generate the tag using dictionary above
        src_tag = [make_tag('frame_info',a, 0,'src_data')]
 
        # initialize the blocks
        lora_sdr_gray_mapping = lora_sdr.gray_mapping(soft_decoding)
        blocks_vector_source = blocks.vector_source_s(src_data, False, 1, src_tag)
        blocks_vector_sink = blocks.vector_sink_s(1, 1024)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_gray_mapping, 0))
        self.tb.connect((lora_sdr_gray_mapping, 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output
        result_data = blocks_vector_sink.data()

        # generate reference data
        ref_data = gray_mapping(src_data)

        self.assertEqual(ref_data, result_data)

if __name__ == '__main__':
    gr_unittest.run(qa_gray_mapping)
