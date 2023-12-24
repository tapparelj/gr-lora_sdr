##############################################################################
# File: qa_whitening.py
# Date: 21-12-2023
#
# Description: This is a test code for block whitening
#
# Function: make_tag
#   Description: Create a GNU Radio tag with specified key, value, offset, and optional source ID.
#   Input: key (str) - Key for the tag, value - Value for the tag, 
#          offset (int) - Offset of the tag in intput data, srcid (optional) - Source ID for the tag, default is None
#   Output: gr.tag_t - GNU Radio tag object with specified attributes
#
# Function: test_001_vector_source
#   Description: test the correctness of generating whitening sequence using vector source
#
# Function: test_002_file_source
#   Description: test the correctness of generating whitening sequence using file source
#
# Function: test_003_whitening_sequence_validation
#   Description: check the whitening sequence in whitening_sequence.py
#
# Function: test_004_edge_test_empty_input
#   Description: check the correctness of whitening block when there is no input 
#
# Function: test_005_is_hex
#   Description: check the correctness of whitening block when the input is hexidecimal
#
# Function: test_006_use_tag_function_test
#   Description: check the adding tag function in whitening block
#
# Function: test_007_use_multiple_tags
#   Description: check adding multiple tags at the beginning of each frame, the frame lengths are defined as 16, 32, 64
##############################################################################


from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
from whitening_sequence import code
import pmt
import numpy as np
import os
import sys

try:
  from gnuradio.lora_sdr import whitening
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    from gnuradio.lora_sdr import whitening


script_dir = os.path.dirname(os.path.abspath(__file__))

def make_tag(key, value, offset, srcid=None):
    tag = gr.tag_t()
    tag.key = pmt.string_to_symbol(key)
    tag.value = pmt.to_pmt(value)
    tag.offset = offset
    if srcid is not None:
        tag.srcid = pmt.to_pmt(srcid)
    return tag

class qa_whitening(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def combine(self, result_data): # combine two nibbles into one symbol
        return [result_data[2 * i] | (result_data[2 * i + 1] << 4) for i in range(int(len(result_data) / 2))]

    def test_001_vector_source(self):

        # set the payload_length        
        payload_length = 5
        # a symbol has 8 bits 
        max_value = 256 
        # randomly generate the source data
        src_data = np.random.randint(max_value, size=payload_length)
        # Append 44 at the end of src_data
        src_data = np.append(src_data, 44) # In ASCII, 44 represents comma. The block stops when it meets the separator ','
        
        # initialize the blocks
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()

        # connect the blocks
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
        self.tb.run()

        # get the output from the connected blocks and combine two nibbles into symbol
        result_data = dst.data()
        result_data = self.combine(result_data)

        # generate reference data
        ref_data = [0] * (len(src_data) - 1)
        ref_data = [src_data[i] ^ code[i] for i in range(len(src_data) - 1)]
        
        self.assertEqual(result_data, ref_data)

    def test_002_file_source(self):
        
        # get input from a file
        relative_path = "../../data/GRC_default/example_tx_source.txt"
        file_path = os.path.join(script_dir, relative_path)

        # initialize the blocks
        src = blocks.file_source(gr.sizeof_char*1, file_path, False, 0, 0)
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()

        # connect the blocks
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = dst.data()
        result_data = [hex(result_data[2 * i] | (result_data[2 * i + 1] << 4)) for i in range(int(len(result_data) / 2))]

        # generate reference data
        with open(file_path, "r") as file:
            file_contents = file.read()
        
        input_string = file_contents.split(",")
        ref_data = []
        for i in range(len(input_string)):
            for word, xor_value in zip(input_string[i], code):
                # Convert the segment and XOR value to integers
                word_xor = hex(ord(word) ^ xor_value)
                ref_data.append(word_xor) 

        self.assertEqual(result_data, ref_data)

    def test_003_whitening_sequence_validation(self):

        # 255 is 11111111, if input data is all 1, 
        # the output should be the flipped version of whitening sequence.
        # the length of whitening sequence is 255
        src_data = [255] * 255 + [44] # In ASCII, 44 represents comma. The block stops when it meets the separator ','
       
        # initialize the blocks
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()

        # connect the blocks
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
        self.tb.run()

        # get the output from the connected blocks 
        result_data = dst.data()
        result_data = self.combine(result_data)

        # generate reference data
        flipped_code = [byte ^ 0xFF for byte in code] # change 0 to 1, 1 to 0
        self.assertEqual(result_data, flipped_code)

    def test_004_edge_test_empty_input(self):

        src_data = ()
        
        # initialize the blocks
        src = blocks.vector_source_b(src_data, False, 1,[])
        lora_sdr_whitening = whitening(False,False,',','packet_len')
        dst = blocks.vector_sink_b()

        # connect the blocks
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = dst.data()
        result_data = self.combine(result_data)

        # generate reference data
        ref_data = [0] * (len(src_data) - 1)
        ref_data = [src_data[i] ^ code[i] for i in range(len(src_data) - 1)]
        
        self.assertEqual(result_data, ref_data)

    def test_005_is_hex(self): # input should be even length

        # get input from a file
        relative_path = "../../data/GRC_default/example_tx_source_ishex.txt"
        file_path = os.path.join(script_dir, relative_path)

        with open(file_path, "r") as file:
            file_contents = file.read()
        input_string = file_contents.split(",")
        result_segments = []
        for i in range(len(input_string)):
            segments = [input_string[i][j:j+2] for j in range(0, len(input_string[i]), 2)]
            
            for segment, xor_value in zip(segments, code):
                # Convert the segment and XOR value to integers
                segment_int = int(segment, 16)
                
                result_int = segment_int ^ xor_value
                result_segments.append(result_int)  

        # initialize the blocks                      
        src = blocks.file_source(gr.sizeof_char*1, file_path, False, 0, 0)
        lora_sdr_whitening = whitening(True,False,',','packet_len')
        dst = blocks.vector_sink_b()

        # connect the blocks
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = dst.data()
        result_data = self.combine(result_data)
    
        self.assertEqual(result_data, result_segments)

    def test_006_use_tag_function_test(self):

        # set the payload_length        
        payload_len = 5
        # a symbol has 8 bits 
        max_value = 256 
        # randomly generate the source data
        src_data = np.random.randint(max_value, size=payload_len)

        # generate the tags
        src_tags = [make_tag('packet_len',payload_len ,0,'src_data')]
        
        # initialize the blocks
        src = blocks.vector_source_b(src_data, False, 1, src_tags)
        lora_sdr_whitening = whitening(False,True,' ','packet_len')
        dst = blocks.vector_sink_b()

        # connect the blocks        
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = dst.data() 
        result_data = self.combine(result_data)
        result_tags = dst.tags()

        # generate reference data
        ref_data = [0] * (len(src_data))
        ref_data = [src_data[i] ^ code[i] for i in range(len(src_data))]

        self.assertEqual(result_data, ref_data)

    def test_007_use_multiple_tags(self):

        payload_len = 112
        max_value = 256 
        # define the three frames' length
        frame_1_len = 16
        frame_2_len = 32
        frame_3_len = 64
        src_data = np.random.randint(max_value, size=payload_len)
        # src_data = np.byte(src_data) # convert to byte values from 0 to 111

        # generate the tags
        src_tags = [make_tag('packet_len', frame_1_len, 0,'src_data'), make_tag('packet_len', frame_2_len, frame_1_len,'src_data'), make_tag('packet_len',frame_3_len,frame_1_len + frame_2_len,'src_data')]

        # initialize the blocks 
        src = blocks.vector_source_b(src_data, False, 1, src_tags)
        lora_sdr_whitening = whitening(False,True,' ','packet_len')
        dst = blocks.vector_sink_b()

        # connect the blocks
        self.tb.connect((src, 0), (lora_sdr_whitening, 0))
        self.tb.connect((lora_sdr_whitening, 0), (dst,0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = dst.data() 
        result_data = self.combine(result_data)

        # generate reference data
        ref_data = [0] * (len(src_data))
        for i in range(frame_1_len):
            ref_data[i] = src_data[i] ^ code[i]
        for i in range(frame_1_len, frame_1_len + frame_2_len):
            ref_data[i] = src_data[i] ^ code[i-16]
        for i in range(frame_1_len + frame_2_len, payload_len):
            ref_data[i] = src_data[i] ^ code[i-48]

        self.assertEqual(result_data, ref_data)
    


if __name__ == '__main__':
    gr_unittest.run(qa_whitening)
