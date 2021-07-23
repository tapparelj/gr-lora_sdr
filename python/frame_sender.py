#!/usr/bin/env python


import numpy
from gnuradio import gr
from loudify import client_api
import time

class frame_sender(gr.sync_block):
    """
    docstring for block frame_sender
    """
    def __init__(self, addres, port, mode):
        verbose = True
        
        self.client = client_api.Client("tcp://"+addres+":"+str(port), verbose)
        self.num_request = 0

        gr.sync_block.__init__(self,
            name="frame_sender",
            in_sig=[(numpy.float32,2)],
            out_sig=None)


    def work(self, input_items, output_items):
        request = b"Hello world"
        try:
            self.client.send(b"echo",  request)
            time.sleep(0.5)
            self.num_request +=1
        except KeyboardInterrupt:
            print("send interrupted, aborting")
            return
        count = 0
        
        while count < self.num_request:
            try:
                reply = self.client.recv()
            except KeyboardInterrupt:
                print("send interrupted, aborting")
                break
            else:
                if reply is None:
                    break
                count += 1

        in0 = input_items[0]
        # <+signal processing here+>
        return len(input_items[0])

