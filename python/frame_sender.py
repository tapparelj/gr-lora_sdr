#!/usr/bin/env python


import numpy
from gnuradio import gr
from loudify import client_sync_api
from loudify import client_async_api
import pmt
import time

from pmt.pmt_swig import length

class frame_sender(gr.sync_block):
    """Frame sender part of the ZMQ client <-> broker <-> worker setup

    Args:
        gr ([type]): [description]
    """

    def __init__(self, addres, port, modus, sf, samp_rate, bw, has_crc, pay_len, cr, impl_head, sync_words):
        verbose = True
        self.modus = modus
        self.send_packet = False
        self.start_index = []
        self.end_index = []
        self.data = numpy.empty([1, 2])
        self.buffer = numpy.empty([1, 2])
        self.sf = sf
        self.samp_rate = samp_rate
        self.bw = bw
        self.has_crc = has_crc
        self.pay_len = pay_len
        self.cr = cr
        self.impl_head = impl_head
        self.sync_words = sync_words

        self.flowgraph_vars ={
            'sf' : self.sf,
            'samp_rate' : self.samp_rate,
            'bw' : self.bw,
            'has_crc': self.has_crc,
            'pay_len' : self.pay_len,
            'cr' : self.cr,
            'impl_head' : self.impl_head,
            'sync_words' : self.sync_words
        }

        if self.modus == True:
            self.client = client_sync_api.Client("tcp://"+addres+":"+str(port), verbose)
        else:
            self.client = client_async_api.Client("tcp://"+addres+":"+str(port), verbose)
            self.num_request = 0

        gr.sync_block.__init__(self,
            name="frame_sender",
            in_sig=[(numpy.float32,2)],
            out_sig=None)


    def work(self, input_items, output_items):

        #copy input data to output
        self.buffer = numpy.concatenate((self.buffer, input_items[0]))

        #search for begin and end tags
        tags = self.get_tags_in_window(0, 0, len(input_items[0]))
        for tag in tags:
            source = pmt.to_python(tag.srcid)
            if source == "frame_detector_timeout" or source == "frame_detector_threshold":
                value = pmt.to_python(tag.value)
                offset = tag.offset

                if value == "start":
                    print("Start offset is ", offset)
                    self.start_index.append(offset)
                elif value == "end":
                    print("End offset is ",offset)
                    self.end_index.append(offset)
                else:
                    print("Error value does not equal start or end")
        
        #if the index of one packet is known get this data
        if len(self.start_index) > 0 and len(self.end_index) > 0:
            start = self.start_index[0]
            end = self.end_index[0]
            print(start, end)
            #TODO : find out how to package the second packet
            self.data = self.buffer[start:end]
            self.send_packet = True
            self.start_index.pop(0)
            self.end_index.pop(0)

        #we have one packet onto sending it onto the network
        if self.send_packet:
            if self.modus == True:
                request = self.data
                reply = self.client.send(b"echo",  request, self.flowgraph_vars)
                if reply:
                    replycode = reply[0]
                    print("Reply from broker")
                else:
                    print("E: no response from broker, make sure it's running")
                self.send_packet = False
            else:
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

