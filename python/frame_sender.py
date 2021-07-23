#!/usr/bin/env python


import numpy
from gnuradio import gr
from loudify import client_sync_api
from loudify import client_async_api
import time

class frame_sender(gr.sync_block):
    """
    docstring for block frame_sender
    """
    def __init__(self, addres, port, modus):
        verbose = True
        self.modus = modus
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

        if self.modus == True:
            request = b"Hello world"
            reply = self.client.send(b"echo",  request)
            if reply:
                print(reply)
                replycode = reply[0]
                print("Reply from broker %s", replycode)
            else:
                print("E: no response from broker, make sure it's running")
            
            in0 = input_items[0]
            # <+signal processing here+>
            return len(input_items[0])
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

