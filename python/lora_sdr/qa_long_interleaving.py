#!/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Long interleaving (SX128x coding rate 4/8LI) and the SF5/SF6 fine-sync symbols.

Reference data come from a real SX1280 (RadioMaster Ranger Micro, ExpressLRS
3.6.3, 2.4 GHz, SF6, 812.5 kHz, CR 4/8LI, implicit header, 8-byte payload, no
LoRa CRC) recorded with an AD9361-based SDR (LiteX-M2SDR). The payload bytes
are ExpressLRS packets whose own CRC14 validates, so they are known exactly.
"""

import os
import time

import numpy as np
import pmt
from gnuradio import blocks, gr, gr_unittest

try:
    from gnuradio import lora_sdr
except ImportError:
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    from gnuradio import lora_sdr

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qa_data")

SF = 6
BW = 812500
PAY_LEN = 8

# (demodulated SF6 symbol values relative to the preamble, payload bytes)
GOLDEN = [
    ([46, 22, 32, 49, 21, 19, 34, 7, 29, 43, 11, 30, 12, 27, 60, 10, 16, 20, 36, 11, 54, 38],
     "2ceac1410d4e4c2f"),
    ([43, 22, 30, 49, 21, 23, 34, 34, 32, 43, 27, 29, 53, 20, 60, 47, 12, 20, 2, 12, 11, 44],
     "a8ebc1410d4e59cb"),
    ([35, 22, 24, 50, 21, 26, 34, 50, 27, 43, 38, 32, 44, 24, 60, 63, 2, 20, 21, 9, 22, 57],
     "60f0c1410d4e08de"),
]


def li_frame_tag(offset, n_symbols):
    """frame_info tag frame_sync emits at the start of a long-interleaving frame."""
    info = pmt.make_dict()
    for key, value in (("is_header", pmt.PMT_T), ("long_interleaving", pmt.PMT_T),
                       ("sf", pmt.from_long(SF)), ("cr", pmt.from_long(4)),
                       ("pay_len", pmt.from_long(PAY_LEN)), ("crc", pmt.PMT_F),
                       ("symb_numb", pmt.from_long(n_symbols)), ("ldro", pmt.PMT_F),
                       ("cfo_int", pmt.from_long(0)), ("cfo_frac", pmt.from_double(0.0))):
        info = pmt.dict_add(info, pmt.intern(key), value)
    return gr.tag_utils.python_to_tag((offset, pmt.intern("frame_info"), info))


class _Burst(gr.basic_block):
    """Emits a list of payloads as messages once, then stays idle."""

    def __init__(self, payloads):
        gr.basic_block.__init__(self, "burst", in_sig=None, out_sig=None)
        self.message_port_register_out(pmt.intern("out"))
        self.payloads = payloads

    def start(self):
        for payload in self.payloads:
            self.message_port_pub(pmt.intern("out"), pmt.intern(payload))
        return True


class qa_long_interleaving(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_002_deinterleave_real_sx1280_symbols(self):
        """Demodulated real SX1280 symbols -> deinterleaver -> Hamming -> dewhitening."""
        symbols, tags = [], []
        for raw, _ in GOLDEN:
            tags.append(li_frame_tag(len(symbols), len(raw)))
            # what gray_mapping hands the deinterleaver: gray(s - 1), as fft_demod outputs s - 1
            symbols += [((s - 1) % 64) ^ (((s - 1) % 64) >> 1) for s in raw]
        src = blocks.vector_source_s(symbols, False, 1, tags)
        deinterleaver = lora_sdr.deinterleaver(False)
        hamming = lora_sdr.hamming_dec(False)
        header = lora_sdr.header_decoder(True, 4, PAY_LEN, False, 0, False)
        dewhitening = lora_sdr.dewhitening()
        sink = blocks.vector_sink_b()
        self.tb.connect(src, deinterleaver, hamming, header, dewhitening, sink)
        self.tb.run()
        expected = b"".join(bytes.fromhex(payload) for _, payload in GOLDEN)
        self.assertEqual(bytes(sink.data()), expected)

    def _loopback(self, fine_sync, soft_decoding=False):
        payloads = ["LI-%04d!" % i for i in range(5)]
        samp_rate = 4 * BW
        burst = _Burst(payloads)
        tx = lora_sdr.lora_sdr_lora_tx(bw=BW, cr=4, has_crc=False, impl_head=True, samp_rate=samp_rate,
                                       sf=SF, ldro_mode=0, frame_zero_padd=1280,
                                       long_interleaving=True, fine_sync=fine_sync)
        rx = lora_sdr.lora_sdr_lora_rx(center_freq=2440000000, bw=BW, cr=4, has_crc=False, impl_head=True,
                                       pay_len=PAY_LEN, samp_rate=samp_rate, sf=SF, soft_decoding=soft_decoding,
                                       ldro_mode=0, print_rx=[False, False],
                                       long_interleaving=True, fine_sync=fine_sync)
        sink = blocks.vector_sink_b()
        self.tb.msg_connect((burst, "out"), (tx, "in"))
        self.tb.connect(tx, rx, sink)
        self.tb.start()
        deadline = time.time() + 10
        while len(sink.data()) < len(payloads) * PAY_LEN and time.time() < deadline:
            time.sleep(0.05)
        self.tb.stop()
        self.tb.wait()
        self.assertEqual(bytes(sink.data()), "".join(payloads).encode())

    def test_003_loopback(self):
        self._loopback(fine_sync=False)

    def test_004_loopback_fine_sync(self):
        self._loopback(fine_sync=True)

    def test_005_loopback_soft_decoding(self):
        self._loopback(fine_sync=True, soft_decoding=True)

    def test_006_real_sx1280_iq(self):
        """Two real SX1280 frames (3.25 MS/s, channel-centred) through the receiver."""
        iq = np.fromfile(os.path.join(DATA_DIR, "sx1280_elrs_sf6_li_2pkt.ci16"), dtype=np.int16)
        samples = (iq[0::2] + 1j * iq[1::2]).astype(np.complex64) / 32768
        # The AD9361 front end of this recording delivers SX128x frames conjugated
        # (the preamble appears as down-chirps); undo that before the LoRa receiver.
        src = blocks.vector_source_c(np.conj(samples).tolist() + [0j] * 20000, False)
        rx = lora_sdr.lora_sdr_lora_rx(center_freq=2455400000, bw=BW, cr=4, has_crc=False, impl_head=True,
                                       pay_len=PAY_LEN, samp_rate=4 * BW, sf=SF, soft_decoding=False,
                                       ldro_mode=0, print_rx=[False, False],
                                       long_interleaving=True, fine_sync=True)
        sink = blocks.vector_sink_b()
        self.tb.connect(src, rx, sink)
        self.tb.run()
        self.assertEqual(bytes(sink.data()).hex(), "a8ebc1410d4e59cb" + "a8ecc1410d4e6664")


if __name__ == "__main__":
    gr_unittest.run(qa_long_interleaving)
