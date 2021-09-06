#!/usr/bin/env python


import numpy
from gnuradio import gr
from loudify import client_sync_api
from loudify import client_async_api
import pmt
import time
import pickle
import pandas as pd
import random
import string 

class frame_sender(gr.sync_block):
    """Frame sender part of the ZMQ client <-> broker <-> worker setup

    Args:
        gr (sync_block): sink block
    """

    def __init__(self, addres, port, modus, debug_mode, reply, sf, samp_rate, bw, has_crc, pay_len, cr, impl_head, sync_words, input_data):
        verbose = True
        self.modus = modus
        self.reply = reply
        self.send_packet = False
        self.start_index = []
        self.end_index = []
        self.data = numpy.empty([0, 2])
        self.buffer = numpy.empty([0, 2])
        self.sf = sf
        self.samp_rate = samp_rate
        self.bw = bw
        self.has_crc = has_crc
        self.pay_len = pay_len
        self.cr = cr
        self.impl_head = impl_head
        self.sync_words = sync_words
        self.input_data = input_data
        # Fix for gr3.9 tags_in_window by using in range with own offset
        self.offset = 0
        self.debug_mode = debug_mode
        self.filename = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

        self.flowgraph_vars = {
            'sf': self.sf,
            'samp_rate': self.samp_rate,
            'bw': self.bw,
            'has_crc': self.has_crc,
            'pay_len': self.pay_len,
            'cr': self.cr,
            'impl_head': self.impl_head,
            'sync_words': self.sync_words
        }

        if self.modus == True:
            self.client = client_sync_api.Client(
                "tcp://" + addres + ":" + str(port), verbose)
        else:
            self.client = client_async_api.Client(
                "tcp://" + addres + ":" + str(port), verbose)
            self.num_request = 0

        if self.debug_mode:
            print("Debug mode is on")
            colum_names_latency = {
                'latency_recieved',
                'latency_decoded',
                'latency_round'
            }
            self.pd_latency = pd.DataFrame(columns=colum_names_latency)
            # Pandas dataframe for packets statistics
            colum_names_packets = {
                'packets_recieved',
                'packets_send',
                'packets_decoded',
            }
            self.pd_packets = pd.DataFrame(columns=colum_names_packets)
            self.num_recieved = 0
            self.num_send = 0
            self.num_decoded = 0

        gr.sync_block.__init__(self,
                               name="frame_sender",
                               in_sig=[(numpy.float32, 2)],
                               out_sig=None)

    def work(self, input_items, output_items):
        """Main function where all the computations happen

        Args:
            input_items (np.complex): the input items of this block
            output_items (None): None

        Returns:
            [type]: [description]
        """
        # copy input data to output
        self.buffer = numpy.concatenate((self.buffer, input_items[0]), axis=0)

        # print("Len input items", len(input_items[0]))
        # print("LEn buffer:", len(self.buffer))
        # print(input_items[0].dtype)
        # print(input_items[0])
        # print(self.buffer.dtype)
        # print(self.buffer)

        # search for begin and end tags
        # Fix for GR3.9 tags_in_window by using in range with own offset
        tags = self.get_tags_in_range(
            0, self.offset, self.offset+len(input_items[0]))
        self.offset += len(input_items[0])
        for tag in tags:
            source = pmt.to_python(tag.srcid)
            if source == "frame_detector_timeout" or source == "frame_detector_threshold":
                # if there is a tag add to the right index
                value = pmt.to_python(tag.value)
                offset = tag.offset
                if value == "start":
                    # print("Start offset is frame_detector ", offset)
                    self.start_index.append(offset)
                elif value == "end":
                    # print("End offset is ", offset)
                    self.end_index.append(offset)
                else:
                    print("Error value does not equal start or end")

        # if the index of one packet is known get this data
        if len(self.start_index) > 0 and len(self.end_index) > 0:
            start = self.start_index[0]
            end = self.end_index[0]
            # print(start, end)
            # TODO : find out how to package the second packet
            self.data = self.buffer[start:end]
            # print("Len packet" , len(self.data))
            # print(self.data)
            # print(self.data.shape)
            self.send_packet = True
            self.start_index.pop(0)
            self.end_index.pop(0)

        # we have one packet onto sending it onto the network
        if self.send_packet:
            if self.modus == True:
                # Sync modus
                request = self.data
                if self.reply:
                    if self.debug_mode:
                        start_timer = time.time_ns()
                        self.num_send += 1
                    reply = self.client.send(b"echo", pickle.dumps(
                        request), flowgraph_vars=self.flowgraph_vars)
                    if reply:
                        print(reply)
                        reply.pop(0)
                        replycode = reply.pop(0)
                        print("I: Reply from broker {}".format(replycode))
                        if self.debug_mode:
                            self.num_recieved += 1
                            # if we are in debug mode measure the time it took to receive the reply
                            end_time = time.time_ns()
                            latency_round = end_time - start_timer
                            latency_data = pickle.loads(reply.pop(0))
                            latency_recieved = latency_data['time_recieved'] - \
                                start_timer
                            latency_decoded = latency_data['time_decoded'] - \
                                start_timer

                            # input data for the pandas dataframe
                            data = {
                                'latency_recieved': latency_recieved / 10**9,
                                'latency_decoded': latency_decoded / 10**9,
                                'latency_round': latency_round / 10**9
                            }
                            self.pd_latency = self.pd_latency.append(
                                data, ignore_index=True)
                            # TODO : maybe random csv for multiple workers ?
                            self.pd_latency.to_csv(self.filename+'_latency.csv')
                            #decode reply code as string and check if reply is same as input
                            reply_msg = str(replycode, "utf-8")[:-1]
                            if reply_msg == self.input_data:
                                self.num_decoded += 1

                            packets_decoded = 1 - \
                                (self.num_decoded / self.num_send)

                            data = {
                                'packets_recieved': self.num_recieved,
                                'packets_send': self.num_send,
                                'packets_decoded': packets_decoded,
                            }
                            self.pd_packets = self.pd_packets.append(data, ignore_index=True)
                            self.pd_packets.to_csv(self.filename+'_packets.csv')

                    else:
                        print("E: no response from broker, make sure it's running")
                else:
                    self.client.send(b"echo", pickle.dumps(
                        request), flowgraph_vars=self.flowgraph_vars)
                self.send_packet = False
            else:
                # Async modus
                request = self.data
                try:
                    self.client.send(b"echo", request,
                                     flowgraph_vars=self.flowgraph_vars)
                    self.num_request += 1
                except KeyboardInterrupt:
                    print("Send interrupted, aborting")
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
