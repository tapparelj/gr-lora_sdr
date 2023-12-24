##############################################################################
# File: qa_dewhitening.py
# Date: 21-12-2023
#
# Description: This is a test code for block dewhitening
#
# Function: make_tag
#   Description: Create a GNU Radio tag with specified key, value, offset, and optional source ID.
#   Input: key (str) - Key for the tag, value - Value for the tag, 
#          offset (int) - Offset of the tag in intput data, srcid (optional) - Source ID for the tag, default is None
#   Output: gr.tag_t - GNU Radio tag object with specified attributes
#
# Function: dewhitening
#   Function: Dewhiten a sequence of source data based on provided parameters.
#   Input:
#     payload_length (int) - Length of the payload,
#     frame_length (int) - Length of the frame,
#     m_crc_presence (int) - Presence indicator for CRC,
#     src_data (list) - Source data to be dewhitened
#   Output:
#     list - Dewhitened data
#
# Function: test_001_functional_test
#   Description: test the correctness of dewhitening when there is no crc
#
# Function: test_002_crc_presence
#    Description: test the correctness of dewhitening when there is crc
##############################################################################

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np

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

def dewhitening(payload_length, frame_length, m_crc_presence, src_data):

    ref_out = []
    offset = 0
    if(m_crc_presence == 0):

        for i in range(payload_length):
            if offset < payload_length:

                low_nib = src_data[2 * i] ^ (code[offset] & 0x0F)
                high_nib = src_data[2 * i + 1] ^( (code[offset] & 0xF0) >> 4)
                ref_out.append(high_nib << 4 | low_nib)
            elif offset < payload_length + 2 and m_crc_presence:
                # Do not dewhiten the CRC
                low_nib = src_data[2 * i]
                high_nib = src_data[2 * i + 1]
                ref_out.append(high_nib << 4 | low_nib)

            else:
                # Full packet received
                break
            
            offset += 1
    else:
        for i in range(int(frame_length/2)):
            if offset < payload_length:
                low_nib = src_data[2 * i] ^ (code[offset] & 0x0F)
                high_nib = src_data[2 * i + 1] ^( (code[offset] & 0xF0) >> 4)
                ref_out.append(high_nib << 4 | low_nib)
            elif offset < payload_length + 2 and m_crc_presence:
                # Do not dewhiten the CRC
                low_nib = src_data[2 * i]
                high_nib = src_data[2 * i + 1]
                ref_out.append(high_nib << 4 | low_nib)

            else:
                # Full packet received
                break
            offset += 1

    return ref_out

class qa_dewhitening(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_function_test(self):

        crc = 0
        # set the payload length randomly 
        payload_len = 10
        # input length is twice the payload which devide a symbol to two nibbles
        frame_len = payload_len* 2
        # the maximum value of the nibble is 15
        max_value = 16
        # randomly generate the nibbles by 
        src_data = np.random.randint(max_value, size=frame_len)

        # generate dictionary 
        a = pmt.make_dict()
        key1 = pmt.intern("pay_len")
        pay_len = pmt.from_long(payload_len)
        key2 = pmt.intern("crc")
        crc_tag = pmt.from_long(crc)
        a = pmt.dict_add(a, key1, pay_len)
        a = pmt.dict_add(a, key2, crc_tag)
        # generate the tag using dictionary above
        src_tag = [make_tag('frame_info',a, 0,'src_data')]

        # initialize the blocks
        lora_sdr_dewhitening = lora_sdr.dewhitening()
        blocks_vector_source = blocks.vector_source_b(src_data, False, 1, src_tag)
        blocks_vector_sink = blocks.vector_sink_b(1, 1024)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_dewhitening, 0))
        self.tb.connect((lora_sdr_dewhitening, 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output
        result_data = blocks_vector_sink.data()

        # generate reference data
        ref_out = dewhitening(payload_len, frame_len, crc, src_data)

        self.assertEqual(result_data, ref_out)

    def test_002_crc_presence(self):

        crc = 1
        # set the payload length randomly 
        payload_len = 10
        # because crc is true the last two symbols are crc
        frame_len = payload_len * 2 + 2  
        # the maximum value of the nibble is 15
        max_value = 16
        # randomly generate the nibbles 
        src_data = np.random.randint(max_value, size=frame_len)

        # generate dictionary
        a = pmt.make_dict()
        key1 = pmt.intern("pay_len")
        pay_len = pmt.from_long(payload_len)
        key4 = pmt.intern("crc")
        crc_tag = pmt.from_long(crc)
        a = pmt.dict_add(a, key1, pay_len)
        a = pmt.dict_add(a, key4, crc_tag)

        # generate the tag using dictionary above
        src_tag = [make_tag('frame_info',a, 0,'src_data')] 

        # initialize the blocks
        lora_sdr_dewhitening = lora_sdr.dewhitening()
        blocks_vector_source = blocks.vector_source_b(src_data, False, 1, src_tag)
        blocks_vector_sink = blocks.vector_sink_b(1, 1024)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_dewhitening, 0))
        self.tb.connect((lora_sdr_dewhitening, 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output
        result_data = blocks_vector_sink.data()

        # generate reference data
        ref_data = dewhitening(payload_len, frame_len, crc, src_data)

        self.assertEqual(result_data, ref_data)
    


if __name__ == '__main__':
    gr_unittest.run(qa_dewhitening)
