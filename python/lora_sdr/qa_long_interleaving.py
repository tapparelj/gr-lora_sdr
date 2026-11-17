#!/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Long interleaving (SX128x coding rates 4/6LI and 4/8LI) and the SF5/SF6 fine-sync symbols.

Reference data come from a real SX1280 (RadioMaster Ranger Micro, 2.4 GHz,
812.5 kHz, implicit header, no LoRa CRC) running ExpressLRS 3.6.3 (SF6) and
4.1.0 (all other modes), recorded with an AD9361-based SDR (LiteX-M2SDR). The
payload bytes are ExpressLRS packets whose own CRC validates, so they are known
exactly.
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

# One real ExpressLRS 4.1.0 frame per packet rate: (sf, cr, symbol values as modulate takes
# them, i.e. relative to the preamble, payload bytes). At SF7 and above the first 8 symbols
# are reduced rate (multiples of 4, plus 1).
REAL_FRAMES = {
    "500 Hz, SF5, 4/6LI, 8 bytes": (5, 2, [23, 22, 31, 19, 13, 22, 19, 3, 6, 12, 27, 22, 4, 6, 18, 22, 12, 30, 7, 24],
                                     "b401c1410d4e60f2"),
    "333 Hz, SF5, 4/8LI, 13 bytes": (5, 4, [2, 7, 3, 17, 2, 22, 12, 23, 0, 14, 10, 29, 5, 11, 0, 24, 25, 26, 0, 17, 18,
                                            12, 3, 20, 2, 16, 11, 26, 26, 18, 28, 20, 15, 21, 8, 5, 7, 24, 1, 6, 14, 8],
                                      "10dcc0021054a0c10724a4506e"),
    "150 Hz, SF7, 4/8LI, 8 bytes": (7, 4, [5, 85, 5, 13, 49, 105, 113, 9, 38, 62, 43, 66, 71, 3, 19, 19, 31, 10, 36, 82,
                                           15],
                                     "f4bac0410d4e26e5"),
    "100 Hz, SF7, 4/8LI, 13 bytes": (7, 4, [21, 37, 121, 77, 25, 17, 13, 33, 104, 82, 22, 39, 25, 81, 55, 39, 57, 91,
                                            107, 66, 91, 127, 112, 66, 37, 78, 87, 88, 23, 49, 16, 110],
                                      "0033806431000000000000df1e"),
    "50 Hz, SF8, 4/8LI, 8 bytes": (8, 4, [165, 85, 129, 197, 209, 181, 133, 89, 148, 75, 121, 236, 67, 165, 0, 252, 47,
                                          22],
                                    "1c29c1410d4e26ab"),
}


def li_frame_tag(offset, n_symbols, sf=SF, cr=4, pay_len=PAY_LEN):
    """frame_info tag frame_sync emits at the start of a long-interleaving frame."""
    info = pmt.make_dict()
    for key, value in (("is_header", pmt.PMT_T), ("long_interleaving", pmt.PMT_T),
                       ("sf", pmt.from_long(sf)), ("cr", pmt.from_long(cr)),
                       ("pay_len", pmt.from_long(pay_len)), ("crc", pmt.PMT_F),
                       ("symb_numb", pmt.from_long(n_symbols)), ("ldro", pmt.PMT_F),
                       ("cfo_int", pmt.from_long(0)), ("cfo_frac", pmt.from_double(0.0))):
        info = pmt.dict_add(info, pmt.intern(key), value)
    return gr.tag_utils.python_to_tag((offset, pmt.intern("frame_info"), info))


def gray_mapped(sf, symbols):
    """What fft_demod and gray_mapping hand the deinterleaver for these symbol values."""
    out = []
    for i, s in enumerate(symbols):
        v = (s - 1) % (1 << sf)  # fft_demod outputs s - 1 ...
        if sf >= 7 and i < 8:
            v //= 4              # ... at reduced rate for the first 8 LI symbols at SF7+
        out.append(v ^ (v >> 1))
    return out


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

    def _deinterleave(self, frames):
        """[(sf, cr, symbols, payload hex)] of one sf/cr -> decoded bytes through deinterleaver ... dewhitening."""
        sf, cr = frames[0][0], frames[0][1]
        symbols, tags = [], []
        for _, _, raw, payload in frames:
            tags.append(li_frame_tag(len(symbols), len(raw), sf, cr, len(payload) // 2))
            symbols += gray_mapped(sf, raw)
        src = blocks.vector_source_s(symbols, False, 1, tags)
        header = lora_sdr.header_decoder(True, cr, len(frames[0][3]) // 2, False, 0, False)
        sink = blocks.vector_sink_b()
        self.tb.connect(src, lora_sdr.deinterleaver(False), lora_sdr.hamming_dec(False), header,
                        lora_sdr.dewhitening(), sink)
        self.tb.run()
        return bytes(sink.data())

    def test_002_deinterleave_real_sx1280_symbols(self):
        """Demodulated real SX1280 symbols -> deinterleaver -> Hamming -> dewhitening."""
        frames = [(SF, 4, raw, payload) for raw, payload in GOLDEN]
        expected = b"".join(bytes.fromhex(payload) for _, payload in GOLDEN)
        self.assertEqual(self._deinterleave(frames), expected)

    def test_007_deinterleave_real_frames_all_rates(self):
        """One real frame per ExpressLRS packet rate: 4/6LI, 13-byte frames, reduced-rate SF7/SF8 symbols."""
        for name, frame in REAL_FRAMES.items():
            with self.subTest(name):
                self.tb = gr.top_block()
                self.assertEqual(self._deinterleave([frame]).hex(), frame[3])

    def test_008_encode_real_frames_all_rates(self):
        """whitening ... gray_demap reproduce the real SX1280 symbols, padding included."""
        for name, (sf, cr, raw, payload) in REAL_FRAMES.items():
            with self.subTest(name):
                tb = gr.top_block()
                burst = _Burst([payload])
                whitening = lora_sdr.whitening(True, False)
                sink = blocks.vector_sink_i()
                tb.msg_connect((burst, "out"), (whitening, "msg"))
                tb.connect(whitening, lora_sdr.header(True, False, cr), lora_sdr.add_crc(False),
                           lora_sdr.hamming_enc(cr, sf, True), lora_sdr.interleaver(cr, sf, 0, BW, True),
                           lora_sdr.gray_demap(sf), sink)
                tb.start()
                deadline = time.time() + 10
                while len(sink.data()) < len(raw) and time.time() < deadline:
                    time.sleep(0.01)
                tb.stop()
                tb.wait()
                self.assertEqual(list(sink.data()), raw)

    def _loopback(self, fine_sync, soft_decoding=False, sf=SF, cr=4, pay_len=PAY_LEN):
        payloads = [("LI-%04d!" % i).ljust(pay_len, "#") for i in range(5)]
        samp_rate = 4 * BW
        burst = _Burst(payloads)
        tx = lora_sdr.lora_sdr_lora_tx(bw=BW, cr=cr, has_crc=False, impl_head=True, samp_rate=samp_rate,
                                       sf=sf, ldro_mode=0, frame_zero_padd=1280,
                                       long_interleaving=True, fine_sync=fine_sync)
        rx = lora_sdr.lora_sdr_lora_rx(center_freq=2440000000, bw=BW, cr=cr, has_crc=False, impl_head=True,
                                       pay_len=pay_len, samp_rate=samp_rate, sf=sf, soft_decoding=soft_decoding,
                                       ldro_mode=0, print_rx=[False, False],
                                       long_interleaving=True, fine_sync=fine_sync)
        sink = blocks.vector_sink_b()
        self.tb.msg_connect((burst, "out"), (tx, "in"))
        self.tb.connect(tx, rx, sink)
        self.tb.start()
        deadline = time.time() + 10
        while len(sink.data()) < len(payloads) * pay_len and time.time() < deadline:
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

    def test_009_loopback_cr46_sf5(self):
        self._loopback(fine_sync=True, sf=5, cr=2)

    def test_010_loopback_cr46_sf5_soft_decoding(self):
        self._loopback(fine_sync=True, soft_decoding=True, sf=5, cr=2)

    def test_011_loopback_sf7_13_bytes(self):
        self._loopback(fine_sync=False, sf=7, pay_len=13)

    def test_012_loopback_sf8_soft_decoding(self):
        self._loopback(fine_sync=False, soft_decoding=True, sf=8)

    def _real_iq(self, name, center_freq, sf, cr, pay_len, fine_sync):
        iq = np.fromfile(os.path.join(DATA_DIR, name), dtype=np.int16)
        samples = (iq[0::2] + 1j * iq[1::2]).astype(np.complex64) / 32768
        # The AD9361 front end of these recordings delivers SX128x frames conjugated
        # (the preamble appears as down-chirps); undo that before the LoRa receiver.
        src = blocks.vector_source_c(np.conj(samples).tolist() + [0j] * 20000, False)
        rx = lora_sdr.lora_sdr_lora_rx(center_freq=center_freq, bw=BW, cr=cr, has_crc=False, impl_head=True,
                                       pay_len=pay_len, samp_rate=4 * BW, sf=sf, soft_decoding=False,
                                       ldro_mode=0, print_rx=[False, False],
                                       long_interleaving=True, fine_sync=fine_sync)
        sink = blocks.vector_sink_b()
        self.tb.connect(src, rx, sink)
        self.tb.run()
        return bytes(sink.data()).hex()

    def test_006_real_sx1280_iq(self):
        """Two real SX1280 frames (3.25 MS/s, channel-centred) through the receiver."""
        self.assertEqual(self._real_iq("sx1280_elrs_sf6_li_2pkt.ci16", 2455400000, SF, 4, PAY_LEN, True),
                         "a8ebc1410d4e59cb" + "a8ecc1410d4e6664")

    def test_013_real_sx1280_iq_sf5_cr46(self):
        """Two real SX1280 frames at SF5, CR 4/6LI (ExpressLRS 500 Hz) through the receiver."""
        self.assertEqual(self._real_iq("sx1280_elrs_sf5_cr46li_2pkt.ci16", 2440400000, 5, 2, 8, True),
                         "b401c1410d4e60f2" + "9401c1410d4e6643")

    def test_014_real_sx1280_iq_sf7_13_bytes(self):
        """Two real 13-byte SX1280 frames at SF7, CR 4/8LI (ExpressLRS 100 Hz Full) through the receiver."""
        self.assertEqual(self._real_iq("sx1280_elrs_sf7_li_13b_2pkt.ci16", 2440400000, 7, 4, 13, False),
                         "0033806431000000000000df1e" + "1042c2021054a0c10724a45eb2")


if __name__ == "__main__":
    gr_unittest.run(qa_long_interleaving)
