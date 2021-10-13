#!/usr/bin/env python


import numpy
from gnuradio import gr
from loudify import definitions
import zmq
import time
import signal
import pickle


class frame_reciever(gr.sync_block):
    """
    docstring for block frame_reciever
    """

    def __init__(self, address, port, service, mode):
        self.verbose = False
        # make a zmq context and connect to the ipc port
        context = zmq.Context()
        self.context = context
        self.socket = context.socket(zmq.PAIR)

        try:
            self.socket.bind("ipc://"+address)
        except zmq.error.ZMQError:
            print("ZMQ error")
        self.buffer = []
        #send correct recv of files
        self.socket.send(definitions.W_REPLY)
        self.state = 1

        gr.sync_block.__init__(self,
                               name="frame_reciever",
                               in_sig=None,
                               out_sig=[(numpy.float32, 2)])

    def work(self, input_items, output_items):
        
        out = output_items[0]
        max_items = len(output_items[0])
        if self.state == 1:
            #get the worker I/Q data
            try:
                data = self.socket.recv()
            except zmq.error.ZMQError:
                print("ZMQ error recv")
            data = pickle.loads(data)
            if self.verbose:
                print("Got data, len", len(data))
            #transform the data to the right type and put in the buffer
            self.buffer = data
            out[:] = numpy.transpose([data[0:max_items, 0], data[0:max_items, 1]])
            self.buffer = numpy.delete(self.buffer, numpy.arange(max_items), axis=0)
            #send correct recv of files
            try:
                self.socket.send(definitions.W_REPLY)
            except zmq.error.ZMQError:
                print("ZMQ error send")
            self.state = 2
            return len(output_items[0])

        if self.state == 2:
            #Empty the buffer in multiple iterations
            items_to_use = max_items
            len_buffer = len(self.buffer)
            if len_buffer < max_items:
                #edge case if there are less items then we can fit, (the exit case)
                #fill the output with empty data
                items_to_use = len_buffer
                data = numpy.transpose([self.buffer[0:items_to_use, 0], self.buffer[0:items_to_use, 1]])
                zeros = numpy.zeros((max_items - items_to_use, 2), dtype="float64")
                # append empty padding after the frame (to fill to entire frame )
                out[:] = numpy.concatenate((data, zeros), axis=0)
                # close ipc connection
                self.socket.close()
                self.context.destroy()
                return -1
            else:
                #Empty part of the buffer to the output and delete those items from the buffer
                out[:] = self.buffer[0:items_to_use]
                numpy.transpose([self.buffer[0:items_to_use, 0], self.buffer[0:max_items, 1]])
                self.buffer = numpy.delete(self.buffer, numpy.arange(max_items), axis=0)

            return len(output_items[0])
