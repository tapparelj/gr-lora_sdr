##############################################################################
# File: qa_demodulate.py
# Date: 24-12-2023
#
# Description: This is a test code for the FFT demodulation block
#
# Function: make_tag
#   Description: Create a GNU Radio tag with specified key, value, offset, and optional source ID
#   Input: key (str) - Key for the tag, value - Value for the tag,
#          offset (int) - Offset of the tag in input data, srcid (optional) - Source ID for the tag, default is None
#   Output: gr.tag_t - GNU Radio tag object with specified attributes
#
# Function: build_upchirp
#   Description: Build an upchirp signal based on specified parameters, refering to 
#                build_upchirp in utilities.h
#   Input: chirp (list) - List to store the chirp signal,
#          id (int) - Identifier for the chirp,
#          sf (int) - Spreading factor,
#          os_factor (optional) - Oversampling factor, default is 1
#   Output: None
#
# Function: build_ref_chirps
#   Description: Build reference upchirp and downchirp signals based on specified parameters, refering to 
#                build_ref_chirps in utilities.h
#   Input: upchirp (list) - List to store the upchirp signal,
#          downchirp (list) - List to store the downchirp signal,
#          sf (int) - Spreading factor,
#          os_factor (optional) - Oversampling factor, default is 1
#   Output: None
#
# Function: generate_reference_output
#   Description: Generate reference demodulation output based on specified parameters.
#   Input: length (int) - Length of the output signal,
#          preamb_samp_cnt (int) - Count of preamble samples,
#          output_offset (int) - Offset for placing the output in the signal,
#          m_sync_words (list) - List of synchronization words,
#          m_preamb_len (int) - Length of the preamble,
#          m_samples_per_symbol (int) - Samples per symbol,
#          sf (int) - Spreading factor,
#          os_factor (int) - Oversampling factor,
#          m_upchirp (list) - Reference upchirp signal,
#          m_downchirp (list) - Reference downchirp signal,
#          src_data (list) - Input data for the demodulator
#   Output: list - Reference demodulation output
#
# Function: test_001_functional_test
#    Description: Test hard-coding scenarios for FFT demodulation.
#
##############################################################################

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from numpy import array
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

def build_upchirp(chirp, id, sf, os_factor=1):

    N = 2 ** sf
    n_fold = int(N * os_factor - id * os_factor)
    for n in range(int(N * os_factor)):
        if n < n_fold:
            chirp[n] = 1.0 + 0.0j
            chirp[n] *= np.exp(2.0j * np.pi * (n * n / (2 * N) / (os_factor ** 2) + (id / N - 0.5) * n / os_factor))
        else:
            chirp[n] = 1.0 + 0.0j
            chirp[n] *= np.exp(2.0j * np.pi * (n * n / (2 * N) / (os_factor ** 2) + (id / N - 1.5) * n / os_factor))

def build_ref_chirps(upchirp, downchirp, sf, os_factor=1):

    N = 2 ** sf
    build_upchirp(upchirp, 0, sf, os_factor)
    for i in range(len(downchirp)):
        downchirp[i] = np.conjugate(upchirp[i])

def generate_reference_output(length, preamb_samp_cnt, output_offset, m_sync_words, m_preamb_len, m_samples_per_symbol, 
                        sf, os_factor, m_upchirp, src_data):

    ref_out = [0j] * length
    if len(m_sync_words) == 1:
        tmp = m_sync_words[0]
        m_sync_words.extend([0, 0])
        m_sync_words[0] = ((tmp & 0xF0) >> 4) << 3
        m_sync_words[1] = (tmp & 0x0F) << 3

    # generate samples of header
    for i in range(m_preamb_len):
        ref_out[output_offset:output_offset + m_samples_per_symbol] = m_upchirp
        
        output_offset += m_samples_per_symbol
        preamb_samp_cnt += m_samples_per_symbol

    # generate samples of payload
    for i in range(len(src_data)):
        temp2_chirp = [0j] * m_samples_per_symbol
        build_upchirp(temp2_chirp, src_data[i], sf, os_factor)
        ref_out[output_offset:output_offset + m_samples_per_symbol] = temp2_chirp
        output_offset += m_samples_per_symbol

    return ref_out

class qa_demodulate(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_hard_coding(self):

        soft_decoding = False
        sf = 7
        cr = 2
        os_factor = 1 # frame_sync has done the down sampling
        ldro = False

        m_preamb_len = 8
        m_number_of_bins = 2 ** sf
        m_samples_per_symbol = m_number_of_bins # frame_sync has done the down sampling
      
        output_offset = 0
        m_sync_words = [8,16] # synchronize words
        m_upchirp = [0j] * m_samples_per_symbol
        m_downchirp = [0j] * m_samples_per_symbol

        # set the payload (symbol) length randomly, demodulator output a block every time, a block contains 6 symbols, here should be multiples of 6.
        payload_length = 12 
        # symbols are integer from 0 to 2^sf - 1
        max_value = 2**sf
        # randomly generate payload
        ref_data = np.random.randint(max_value, size=payload_length) 
        preamble_data = [31,31,31,31,31,31,31,31] # there are 8 symbols in preamble, in the output they are 31

        # dictionary for header in tag
        a = pmt.make_dict()
        key1 = pmt.intern("is_header")
        is_header = pmt.from_bool(True)
        key2 = pmt.intern("cfo_int")
        cfo_int = pmt.from_long(0)
        key3 = pmt.intern("cfo_frac")
        cfo_frac = pmt.from_float(0)
        key4 = pmt.intern("sf")
        sf_tag = pmt.from_double(sf)
        a = pmt.dict_add(a, key1, is_header)
        a = pmt.dict_add(a, key2, cfo_int)
        a = pmt.dict_add(a, key3, cfo_frac)
        a = pmt.dict_add(a, key4, sf_tag)

        # dictionary for information symbols in tag
        b = pmt.make_dict()
        key1 = pmt.intern("is_header")
        is_header = pmt.from_bool(False)
        key2 = pmt.intern("cr")
        cfo_int = pmt.from_long(cr)
        key3 = pmt.intern("ldro")
        cfo_frac = pmt.from_bool(ldro)
        key4 = pmt.intern("symb_numb")
        sf_tag = pmt.from_long(payload_length)
        b = pmt.dict_add(b, key1, is_header)
        b = pmt.dict_add(b, key2, cfo_int)
        b = pmt.dict_add(b, key3, cfo_frac)
        b = pmt.dict_add(b, key4, sf_tag)

        # make the tag
        src_tag = [make_tag('frame_info',a, 0,'src_data'), make_tag('frame_info',b, m_preamb_len*m_samples_per_symbol,'src_data')]
        
        # generate src_data by using ref_data and do fft
        length = (m_preamb_len + payload_length) * m_samples_per_symbol
        src_data = [0j] * length
        preamb_samp_cnt = 0
        build_ref_chirps(m_upchirp, m_downchirp, sf, os_factor)
        src_data = generate_reference_output(length, preamb_samp_cnt, output_offset, m_sync_words, m_preamb_len, m_samples_per_symbol, sf, os_factor, m_upchirp, ref_data)

        # initialize the blocks
        lora_sdr_fft_demod = lora_sdr.fft_demod(soft_decoding, False)
        blocks_vector_source = blocks.vector_source_c(src_data, False, 1, src_tag)
        blocks_vector_sink = blocks.vector_sink_s(1, 1024)

        # connect the blocks
        self.tb.connect((blocks_vector_source, 0), (lora_sdr_fft_demod, 0))
        self.tb.connect((lora_sdr_fft_demod, 0), (blocks_vector_sink, 0))
        self.tb.run()

        # get the output from the connected blocks
        result_data = blocks_vector_sink.data()

        # in fft_demod_impl.cc, it shifts by -1 and uses reduce rate if first block (header)
        ref_data = ref_data - 1 
        ref_out =np.concatenate((preamble_data , ref_data), axis=0)

        for i in range(len(ref_out)):
            self.assertEqual(result_data[i], ref_out[i])

if __name__ == '__main__':
    gr_unittest.run(qa_demodulate)
