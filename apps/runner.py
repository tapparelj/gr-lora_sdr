import threading
import pickle
import zmq
import sys
import ast
from loudify import worker_api
from loudify import definitions
import cran_recieve
from threading import Thread
import time

def main():

    def start_flowgraph(flowgraph_vars, results, index):
        """
        Starts the actual flowgraph (cran_recieve.py) in a seperate thread

        :param flowgraph_vars: dict containing the flowgraph vars
        :param results: results list
        :param index: index to store the value of the thread in
        :return:
        """
        msg = cran_recieve.main(flowgraph_vars)
        results[index] = msg

    reply = None
    max_threads = 10
    threads = [None] * max_threads
    results = [None] * max_threads
    addres = "localhost"
    port = 5555
    service = "echo"
    verbose = True
    worker = worker_api.Worker("tcp://"+addres+":"+str(port), str(service).encode(), verbose)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("ipc://6270")

    while True:
        request = worker.recv(reply)
        if request is None:
            print("Worker was interrupted")
        if request:
            
            print("Got a request")
            data = request.pop(0)
            input_data = data
            index = 1
            #convert back to dict
            flowgraph_vars = ast.literal_eval(request.pop(0).decode('utf-8'))
            threads[index] = Thread(target=start_flowgraph, args=(flowgraph_vars, results, index))
            threads[index].start()
            socket.send(input_data)
            socket.recv()
            threads[index].join(definitions.Rx_timeout)
            #if there is a result send result back else send back an error code
            if results[index] is not None:
                reply = [results[index].encode()]
            else:
                reply = [definitions.W_ERROR]



if __name__ == '__main__':
    main()