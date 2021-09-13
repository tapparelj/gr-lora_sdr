"""C-RAN Runner file."""
import pickle
import zmq
import ast
from loudify import worker_api, definitions
import subprocess
import codecs
import time
import os
import random
import string


def generate_pipe():
    """
    Generate a random pipe for the worker to connect to.

    Returns:
        string: path of a pipe
    """
    pipe = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    pipe = "/tmp/"+pipe
    return pipe

def main():
    """
    Main function that starts the C-RAN server."""

    reply = None
    service = "echo"
    verbose = True
    latency = True
    # connect to the broker using the worker_api
    if os.environ.get('CONNECT') is not None:
        print(os.environ.get('CONNECT'))
        worker = worker_api.Worker(os.environ.get(
            'CONNECT'), str(service).encode(), verbose)
    else:
        addres = "0.0.0.0"
        port = 5555
        worker = worker_api.Worker(
            "tcp://"+addres+":"+str(port), str(service).encode(), verbose)
    # connec to the flowgraph using zmq pairs
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    
    pipe = generate_pipe()
    while os.path.isfile(pipe):
        pipe = generate_pipe()

    socket.connect("ipc://"+pipe)
    #Run main function recieve network packets and forward them to GNU Radio
    while True:
        request = worker.recv(reply)
        if request is None:
            exit(0)
        if request:
            if latency:
                time_recieved = time.time_ns()
            data = request.pop(0)
            input_data = data
            # convert back to dict
            flowgraph_vars = ast.literal_eval(request.pop(0).decode('utf-8'))
            vars = codecs.encode(pickle.dumps(
                flowgraph_vars), "base64").decode()
 
            # send the vars to the flowgraph and execute it
            p = subprocess.Popen(["./cran_recieve.py", vars, pipe],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # send I/Q data to the flowgraph
            socket.send(input_data)
            # wait for reply from flowgraph
            reply = socket.recv()
            try:
                out, err = p.communicate(timeout=definitions.TIMEOUT)
                # print(out,err)
                out2 = out
                # send back the last part of the split of the output (decoded msg) from crc_verify
                msg = out2.decode("utf-8").split(":")[-1]

                if latency:
                    # if we are messuring the latency put all the latency data and send it
                    latency_data = {
                        'time_recieved': time_recieved,
                        'time_decoded': time.time_ns()
                    }
                    reply = [msg.encode(), pickle.dumps(latency_data)]
                else:
                    reply = [msg.encode()]
                p.kill()
            except subprocess.TimeoutExpired:
                # if decoding took to long
                if latency:
                    # if we are messuring the latency put all the latency data and send it
                    latency_data = {
                        'time_recieved': time_recieved,
                        'time_decoded': time.time_ns()
                    }
                    reply = [definitions.W_ERROR, pickle.dumps(latency_data)]
                else:
                    reply = [definitions.W_ERROR]
                p.kill()
            p.kill()


if __name__ == '__main__':
    main()
