#!/usr/bin/env python


import numpy
from gnuradio import gr
import zmq
import time
import signal
import pickle

class frame_reciever(gr.sync_block):
    """
    docstring for block frame_reciever
    """
    def __init__(self, addres, port, service, mode):
        verbose  = True
        

        #make a worker context
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://localhost:6270")
        self.buffer =[]
        self.state = 1
        
        gr.sync_block.__init__(self,
            name="frame_reciever",
            in_sig=None,
            out_sig=[(numpy.float32,2)])


    def work(self, input_items, output_items):
        out = output_items[0]
        max_items = len(output_items[0])
        if self.state == 1:
            print(len(output_items[0]))
            data = self.socket.recv()
            data = pickle.loads(data)
            print(data.shape)
            print(data.size)
            out[:] = numpy.transpose([data[0:max_items,0],data[0:max_items,1]])
            self.buffer = data[max_items+1:]
            # out = output_items[0]
            # # <+signal processing here+>
            # # out[0] = 1+2j
            print("recieved frame")
            self.state = 2
            return len(output_items[0])
        
        if self.state == 2:
            print("emptying frame")
            print(max_items)
            items_to_use = max_items
            len_buffer = len(self.buffer)
            if len_buffer < max_items :
                items_to_use = len_buffer
                print(max_items-items_to_use)
                #append empty padding after the frame (to fill to entire frame )
                out[:] = numpy.concatenate((self.buffer[0:items_to_use], numpy.zeros((max_items-items_to_use,2),dtype=complex)),axis=0)
                self.state = 1
            else:
                out[:] = self.buffer[0:items_to_use]
                numpy.transpose([self.buffer[0:items_to_use,0],self.buffer[0:max_items,1]])
                self.buffer = self.buffer[items_to_use+1:]
            print(items_to_use, max_items)
            print(self.buffer.shape)

            #TODO find out why in the end it will not work
            return len(output_items[0])
