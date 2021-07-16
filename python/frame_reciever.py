#!/usr/bin/env python


import numpy
from gnuradio import gr
from loudify_worker import worker_api

class frame_reciever(gr.sync_block):
    """
    docstring for block frame_reciever
    """
    def __init__(self, addres, port, mode):
        verbose  = True
        print(addres,port,mode)

        #make a worker context
        self.worker = worker_api.Worker("tcp://localhost:5555", b"echo", verbose)
        
        gr.sync_block.__init__(self,
            name="frame_reciever",
            in_sig=None,
            out_sig=[(numpy.float32,2)])


    def work(self, input_items, output_items):
        reply = None
        while True:
            request = self.worker.recv(reply)
            # sleep(0.025)
            if request is None:
                print("Worker was interrupted")
                break  # Worker was interrupted
            reply = request  # Echo is complex... :-)

        out = output_items[0]
        # <+signal processing here+>
        out[0] = numpy.array([1+2j, 3+4j, 5+6j])
        return len(output_items[0])

