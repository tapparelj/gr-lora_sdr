##############################################################################
# File: qa_interleaver.py
# Date: 24-12-2023
#
# Description: This is a test code for block interleaver
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
# Function: interleaver
#     Description: Perform interleaving on input data based on specified parameters.
#   Input:
#     in_data (list): Input data to be interleaved.
#     m_sf (int): Spreading factor.
#     m_cr (int): Coding rate.
#     m_ldro (bool): Indicator for low-density parity-check code rate.
#     m_frame_len (int): Length of the frame.
#   Output:
#     list: Interleaved output data.
#
# Function: test_001_functional_test
#   Description: test the correctness of decoding hamming parity in hardcoding
#               when input is not header
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
    tag.value = pmt.to_pmt(value)
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

def interleaver(in_data, m_sf, m_cr, m_ldro, m_frame_len):
    
    nitems_to_process = len(in_data)
    out_data = []
    cw_cnt = 0
    
    while cw_cnt in range(m_frame_len):
    
        cw_len = 4 + (4 if cw_cnt< m_sf - 2 else m_cr)
        sf_app = m_sf - 2 if (cw_cnt < m_sf - 2) or m_ldro else m_sf
        print(sf_app)
        nitems_to_process = np.minimum(nitems_to_process,sf_app)

        if nitems_to_process >= sf_app or cw_cnt + nitems_to_process == m_frame_len :

            # Create the empty matrices
            cw_bin = [int2bool(0, cw_len) for _ in range(sf_app)]
            init_bit = [0] * m_sf
            inter_bin = [init_bit.copy() for _ in range(cw_len)]

            # Convert input codewords to binary vector of vector
            for i in range(sf_app):
                if i >= nitems_to_process:
                    cw_bin[i] = int2bool(0, cw_len)
        
                else:
                    cw_bin[i] = int2bool(in_data[i], cw_len)
              
                cw_cnt += 1
                
            for i in range(cw_len):
                for j in range(sf_app):
                    inter_bin[i][j] = cw_bin[mod((i - j - 1), sf_app)][i]
                
                # For the first block, add a parity bit and a zero at the end of the LoRa symbol (reduced rate)
                if cw_cnt == m_sf - 2 or m_ldro:
                    inter_bin[i][sf_app] = sum(inter_bin[i]) % 2
              
                out_data.append(bool2int(inter_bin[i]))
            in_data = in_data[nitems_to_process:]
            nitems_to_process = m_frame_len - nitems_to_process # consume the items

    return out_data

class qa_interleaver(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        sf = 7
        cr = 2
        ldro = False
        # define payload length which should be (sf-2) + n * sf
        payload_length = 12
        # the symbol is composed of 8 bits
        max_value = 2 ** sf
        # randomly generate the input data
        src_data = np.random.randint(max_value, size=payload_length)

        # make the tag
        src_tags = [make_tag('frame_len',payload_length, 0,'src_data')] 
        
        # initialize the blocks
        blocks_vector_source = blocks.vector_source_b(src_data, False, 1, src_tags)
        lora_sdr_interleaver = lora_sdr.interleaver(cr, sf, ldro, 125000)
        blocks_vector_sink = blocks.vector_sink_i(1, 1024)  

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_interleaver, 0))
        self.tb.connect((lora_sdr_interleaver , 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = blocks_vector_sink.data()

        # generate reference interleaver
        ref_out = interleaver(src_data, sf, cr,ldro, payload_length)

        self.assertEqual(result_data, ref_out)

    
if __name__ == '__main__':
    gr_unittest.run(qa_interleaver)