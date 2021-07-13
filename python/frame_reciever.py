#!/usr/bin/env python


import numpy
from gnuradio import gr

class frame_reciever(gr.sync_block):
    """
    docstring for block frame_reciever
    """
    def __init__(self, addres, port, mode):
        gr.sync_block.__init__(self,
            name="frame_reciever",
            in_sig=None,
            out_sig=[<+numpy.float32+>, ])


    def work(self, input_items, output_items):
        out = output_items[0]
        # <+signal processing here+>
        out[:] = whatever
        return len(output_items[0])

