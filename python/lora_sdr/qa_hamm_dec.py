##############################################################################
# File: qa_hamm_dec.py
# Date: 21-12-2023
#
# Description: This is a test code for block hamming_decoding
#
# Function: make_tag
#   Description: Create a GNU Radio tag with specified key, value, offset, and optional source ID.
#   Input: key (str) - Key for the tag, value - Value for the tag, 
#          offset (int) - Offset of the tag in intput data, srcid (optional) - Source ID for the tag, default is None
#   Output: gr.tag_t - GNU Radio tag object with specified attributes
#
# Function: int2bool
#   Description:convert an integer (value) into a list of boolean values, 
#            where each boolean represents a bit in the binary representation 
#            of the integer. The function 
#   Input: the integer value, num_bits(the number of bits)  
#   Output: list - a list of boolean values representing the binary
#
# Function: bool2int
#   Description: Convert a binary representation (list of boolean values) to an integer.
#   Input:
#     b (list) - Binary representation as a list of boolean values
#   Output:
#     int - Integer representation of the binary input
#
# Function: hamm_dec
#   Description: Perform Hamming decoding on input data based on specified parameters.
#   Input:
#     cr (int) - Coding rate,
#     in_data (list) - Input data to be decoded,
#     is_header (bool) - Indicator for header decoding
#   Output:
#     list - Decoded data after Hamming decoding
#
# Function: test_001_functional_test
#    Description: test the correctness of decoding hamming parity in hardcoding
#               when input is not header
##############################################################################

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
import pmt
import numpy as np
from functools import reduce

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

def int_to_bool(value, num_bits):
    return [(value >> i) & 1 for i in range(num_bits - 1, -1, -1)]

def bool_to_int(b):
    return reduce(lambda x, y: (x << 1) + y, b, 0)

def hamm_dec(cr, in_data, is_header):
    out_data = []
    cr_app = 4 if is_header else cr

    for i in range(len(in_data)):
        data_nibble = [False] * 4
        s0, s1, s2 = False, False, False
        syndrom = 0

        codeword = int_to_bool(in_data[i], cr_app + 4)
        
        data_nibble = [codeword[3], codeword[2], codeword[1], codeword[0]]  # reorganized msb-first

        if cr_app == 4:
            if not (sum(codeword) % 2): 
                continue

        elif cr_app == 3:
            # get syndrom
            s0 = codeword[0] ^ codeword[1] ^ codeword[2] ^ codeword[4]
            s1 = codeword[1] ^ codeword[2] ^ codeword[3] ^ codeword[5]
            s2 = codeword[0] ^ codeword[1] ^ codeword[3] ^ codeword[6]

            syndrom = s0 + (s1 << 1) + (s2 << 2)

            if syndrom == 5:
                data_nibble[3] = not data_nibble[3]
            elif syndrom == 7:
                data_nibble[2] = not data_nibble[2]
            elif syndrom == 3:
                data_nibble[1] = not data_nibble[1]
            elif syndrom == 6:
                data_nibble[0] = not data_nibble[0]

        elif cr_app == 2:
            s0 = codeword[0] ^ codeword[1] ^ codeword[2] ^ codeword[4]
            s1 = codeword[1] ^ codeword[2] ^ codeword[3] ^ codeword[5]

            if s0 or s1:
                pass 

        elif cr_app == 1:
            if not (sum(codeword) % 2):
                pass 

        out_data.append(bool_to_int(data_nibble))

    return out_data

class qa_hamm_dec(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        sf = 7
        cr = 2
        # set the payload length randomly
        payload_length = 10
        # a symbol is 8 bits
        max_value = 256
        # randomly generate the nibbles output by whitening block
        src_data = np.random.randint(max_value, size=payload_length)
        soft_decoding = False
        is_header = False

        # generate dictionary containing information of the header 
        a = pmt.make_dict()
        key1 = pmt.intern("is_header")
        is_header_tag = pmt.from_bool(is_header)
        key2 = pmt.intern("cr")
        cr_tag = pmt.from_long(cr)
        a = pmt.dict_add(a, key1, is_header_tag)
        a = pmt.dict_add(a, key2, cr_tag)

        # make the tag
        src_tag = [make_tag('frame_info',a, 0,'src_data')]

        # initialize the blocks
        lora_sdr_hamming_dec = lora_sdr.hamming_dec(soft_decoding)
        blocks_vector_source = blocks.vector_source_b(src_data, False, 1, src_tag)
        blocks_vector_sink = blocks.vector_sink_b(1, 1024)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_hamming_dec, 0))
        self.tb.connect((lora_sdr_hamming_dec, 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = blocks_vector_sink.data()
    
        # generate reference data
        ref_out = hamm_dec(cr, src_data, is_header)

        self.assertEqual(ref_out, result_data)

    

if __name__ == '__main__':
    gr_unittest.run(qa_hamm_dec)
