##############################################################################
# File: qa_deinterleaver.py
# Date: 21-12-2023
#
# Description: This is a test code for block deinterleaver, here we only consider hardcoding
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
#   Function: Convert a binary representation (list of boolean values) to an integer.
#   Input:
#     b (list) - Binary representation as a list of boolean values
#   Output:
#     int - Integer representation of the binary input
#
# Function: deinterleave
#   Function: deinterleave input data for encoding based on specified parameters.
#   Input:
#     in_data (list) - Input data to be processed,
#     sf (int) - Spreading factor,
#     cr (int) - Coding rate,
#     ldro (bool) - LDRO (Low Density Parity Check Code) presence indicator,
#     m_frame_len (int) - Length of the frame
#   Output:
#     list - Processed data for encoding
#
# Function: test_001_functional_test
#    Description: test the correctness of de-interleaving
##############################################################################


from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
import pmt
import numpy as np
import os
import sys

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

import numpy as np

def int2bool(integer, n_bits):
    vec = [(integer >> i) & 1 for i in range(n_bits - 1, -1, -1)]

    return vec

def bool2int(b):
    integer = sum(bit << i for i, bit in enumerate(reversed(b)))
    return integer

def mod(a, b):
    return a % b

def deinterleave(in_data, sf, cr, ldro, m_frame_len):

    # first generate the header
    out = []
    is_header = True
    sf_header = sf - 2 if is_header or ldro else sf
    cw_len = 8 if is_header else cr + 4 # cw_len symbols per block

    inter_bin = [int2bool(in_data[j], sf_header) for j in range(cw_len)]
    init_bit = [0] * cw_len
    deinter_bin = [init_bit.copy() for _ in range(sf_header)]

    for b in range(cw_len):
        for c in range(sf_header):
            deinter_bin[mod((b - c - 1), sf_header)][b] = inter_bin[b][c]

    for d in range(sf_header):
        out.append(bool2int(deinter_bin[d]))

    # then generate the payload
    is_header = False
    sf_payload = sf - 2 if is_header or ldro else sf
    cw_len = 8 if is_header else cr + 4
    
    for i in range(int((m_frame_len-8) / cw_len)):

        inter_bin = [int2bool(in_data[i*cw_len+j+8], sf_payload) for j in range(cw_len)]
        init_bit = [0] * cw_len
        deinter_bin = [init_bit.copy() for _ in range(sf_payload)]

        for b in range(cw_len):
            for c in range(sf_payload):
                deinter_bin[mod((b - c - 1), sf_payload)][b] = inter_bin[b][c]

        for d in range(sf_payload):
            out.append(bool2int(deinter_bin[d]))


    return out


class qa_deinterleaver(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        sf = 7
        cr = 2
        ldro = 0
        soft_decoding = False
        # set payload length
        payload_len = 42
        # input data is 8 symbol header followed by payload
        frame_len = payload_len + 8 
        # the symbol is composed of 8 bits
        max_value = 256

        # generate dictionary containing information of the header 
        a = pmt.make_dict()
        key1 = pmt.intern("is_header")
        is_header_tag = pmt.from_bool(1)
        key2 = pmt.intern("sf")
        sf_tag = pmt.from_long(sf)

        a = pmt.dict_add(a, key1, is_header_tag)
        a = pmt.dict_add(a, key2, sf_tag)

        # generate dictionary containing information of the payload
        b = pmt.make_dict()
        key1 = pmt.intern("is_header")
        is_header_tag_b = pmt.from_bool(0)
        key2 = pmt.intern("ldro")
        ldro_tag = pmt.from_bool(ldro)
        key3 = pmt.intern("cr")
        cr_tag = pmt.from_long(cr)

        b = pmt.dict_add(b, key1, is_header_tag_b)
        b = pmt.dict_add(b, key2, ldro_tag)
        b = pmt.dict_add(b, key3, cr_tag)

        # randomly generate the input data
        src_data = np.random.randint(max_value, size=frame_len)

        # make the tag
        src_tags = [make_tag('frame_info',a, 0,'src_data'),make_tag('frame_info',b, 8,'src_data')] 

        # initialize the blocks
        blocks_vector_source = blocks.vector_source_s(src_data, False, 1, src_tags)
        lora_sdr_deinterleaver = lora_sdr.deinterleaver(soft_decoding)
        blocks_vector_sink = blocks.vector_sink_b(1, 1024)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_deinterleaver, 0))
        self.tb.connect((lora_sdr_deinterleaver, 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = blocks_vector_sink.data()

        # generate reference interleaver
        ref_out = deinterleave(src_data, sf, cr,ldro, frame_len)

        self.assertEqual(result_data, ref_out)

    
if __name__ == '__main__':
    gr_unittest.run(qa_deinterleaver)