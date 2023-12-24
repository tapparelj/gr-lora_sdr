##############################################################################
# File: qa_add_crc.py
# Date: 24.12.2023
#
# Description: This is a test code for block add_crc
#
# Function: make_tag
#   Description: Create a GNU Radio tag with specified key, value, offset, and optional source ID.
#   Input: key (str) - Key for the tag, value - Value for the tag, 
#          offset (int) - Offset of the tag in input data, srcid (optional) - Source ID for the tag, default is None
#   Output: gr.tag_t - GNU Radio tag object with specified attributes
#
# Function: crc16 
#   Description: Calculate CRC-16 value for a given new_byte and current CRC value,
#                 refering to add_crc_impl.cc
#   Input: crc_value (int) - Current CRC value, new_byte (char) - New byte to update CRC value
#   Output: int - Updated CRC value
#
# Function: calculate_crc
#   Description: Calculate CRC nibbles for a given payload using CRC-16, 
#                refering to add_crc_impl.cc
#   Input: payload (str) - Payload for CRC calculation
#   Output: list - List of CRC nibbles
#
# Function: test_001_functional_test
#    Description: Test the correctness of the add_crc block by comparing the result with the reference CRC nibbles.
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

def crc16(crc_value, new_byte):
    # Assuming new_byte is a character
    byte_value = ord(new_byte) & 0xFF
  
    for i in range(8):
        if ((crc_value & 0x8000) >> 8) ^ (byte_value & 0x80):
            crc_value = (crc_value << 1) ^ 0x1021
        else:
            crc_value = (crc_value << 1)
        byte_value <<= 1
        byte_value = byte_value & 0xFF
        
    return crc_value & 0xffff

def calculate_crc(payload):
    crc = 0x0000
    payload_len = len(payload)

    # Calculate CRC on the N-2 first data bytes using Poly=1021 Init=0000
    for i in range(payload_len - 2):    
        crc = crc16(crc, payload[i])
    crc = crc ^ ord(payload[payload_len - 1]) ^( ord(payload[payload_len - 2]) << 8) 
    crc_nibbles = [
        (crc & 0x000F),
        ((crc & 0x00F0) >> 4),
        ((crc & 0x0F00) >> 8),
        ((crc & 0xF000) >> 12)
    ]

    return crc_nibbles

class qa_add_crc(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_functional_test(self):

        has_crc = True
        # set the payload_length
        payload_len = 6
        # a nibble has 4 bits so that the maximum value for the nibble is 15
        max_value = 16
        # randomly generate the input data of whitening block, because we need to generate tag
        src = np.random.randint(max_value, size=payload_len)
        src_data_str = ''.join(map(str, src))
        # whitening block doubles the length add 5 byte of header 
        frame_len = payload_len * 2 + 5 
        # we don't care how whitening and add header block operate, so generate the source randomly without considering src above
        src_data= np.random.randint(max_value, size=frame_len)

        # generate the tags
        src_tags = [make_tag('frame_len', frame_len, 0,'src_data'),make_tag('payload_str', src_data_str, 0,'src')] 

        # initialize the blocks
        lora_sdr_add_crc = lora_sdr.add_crc(has_crc)
        blocks_vector_source = blocks.vector_source_b(src_data, False, 1, src_tags)
        blocks_vector_sink = blocks.vector_sink_b(1, 2048)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_add_crc , 0))
        self.tb.connect((lora_sdr_add_crc , 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = blocks_vector_sink.data()
        
        # generate crc 
        ref_crc = calculate_crc(src_data_str)

        self.assertEqual(result_data[len(result_data)-4:len(result_data)], ref_crc)

    
if __name__ == '__main__':
    gr_unittest.run(qa_add_crc)