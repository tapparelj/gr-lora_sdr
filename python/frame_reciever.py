#!/usr/bin/env python


import numpy
from gnuradio import gr
from loudify import worker_api
from loudify import definitions
import time
import signal

class frame_reciever(gr.sync_block):
    """
    docstring for block frame_reciever
    """
    def __init__(self, addres, port, service, mode):
        verbose  = True
        

        #make a worker context
        self.worker = worker_api.Worker("tcp://"+addres+":"+str(port), str(service).encode(), verbose)
        
        gr.sync_block.__init__(self,
            name="frame_reciever",
            in_sig=None,
            out_sig=[(numpy.float32,2)])


    def work(self, input_items, output_items):
        reply = None
        out = output_items[0]
        while True:
            request = self.worker.recv(reply)
            if request is None:
                print("Worker was interrupted")
            
            if request:
                data = request.pop(0) 
                flowgraph_vars = request.pop(0)
                #TODO : find out what to do with flowgraph vars
                out = data
                print("Outputting..")
                print(len(out))


            
            # out = output_items[0]
            # # <+signal processing here+>
            # # out[0] = 1+2j

            return len(output_items[0])

