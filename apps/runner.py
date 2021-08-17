import threading
import pickle
import zmq
import sys
import ast
from loudify import worker_api
import cran_recieve
from threading import Thread

class Runnner: 
    
    def __init__(self) -> None:
        self.msg = None
        self.main()


    def main(self):

        def start_flowgraph(sf, results, index):
            msg = cran_recieve.main(sf)
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
                print(flowgraph_vars)
                sf = flowgraph_vars['sf']
                threads[index] = Thread(target=start_flowgraph, args=(sf, results, index))
                threads[index].start()
                socket.send(input_data)
                reply_cran = socket.recv()
                print(reply_cran)
                threads[index].join()
                print("After join")
                print(results)
                reply = ["reply".encode()]


if __name__ == '__main__':
    Runnner()