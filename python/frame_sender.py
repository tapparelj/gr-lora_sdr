#!/usr/bin/env python


import numpy
from gnuradio import gr

class frame_sender(gr.sync_block):
    """
    docstring for block frame_sender
    """
    def __init__(self, addres, port, mode):
        gr.sync_block.__init__(self,
            name="frame_sender",
            in_sig=[<+numpy.float32+>, ],
            out_sig=None)


    def work(self, input_items, output_items):
        in0 = input_items[0]
        # <+signal processing here+>
        return len(input_items[0])

