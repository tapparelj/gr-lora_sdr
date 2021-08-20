import threading
import pickle
import zmq
import sys
import ast
from loudify import worker_api
from loudify import definitions
import threading
import cran_recieve
import subprocess
import codecs
import re
import time
def main():

    # def start_flowgraph(flowgraph_vars, results, threads,index):
    #     """
    #     Starts the actual flowgraph (cran_recieve.py) in a seperate thread

    #     :param flowgraph_vars: dict containing the flowgraph vars
    #     :param results: results list
    #     :param index: index to store the value of the thread in
    #     :return:
    #     """
    #     # newpid=os.fork()
    #     # print(newpid)
    #     # print("new start")
    #     msg = cran_recieve.main(flowgraph_vars)
    #     results[index] = msg
    #     print(msg)
    #     exit(0)

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
    socket.connect("tcp://localhost:6270")
    index = 1

    while True:
        request = worker.recv(reply)
        if request is None:
            print("Worker was interrupted")
        if request:
            
            print("Got a request")
            print(index)
            print(threading.active_count())
            print(threading.enumerate())
            data = request.pop(0)
            input_data = data
            #convert back to dict
            flowgraph_vars = ast.literal_eval(request.pop(0).decode('utf-8'))
            vars = codecs.encode(pickle.dumps(flowgraph_vars), "base64").decode()
            # vars = 
            print(vars)
            print("start")
            myoutput = open('debug.txt', 'w')
            p = subprocess.Popen(["./cran_recieve.py", vars], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # pickle.dump(flowgraph_vars, p.stdin)
            time.sleep(1)
            socket.send(input_data)
            reply = socket.recv()
            print(reply)
            if index ==4:
                for stdout_line in iter(p.stdout.readline, ""):
                    print(stdout_line) 
            # p.stdout.close()
            # return_code = p.wait()
            # if return_code:
            #     raise subprocess.CalledProcessError(return_code, cmd)]
            try : 
                out, err = p.communicate()
                out2 = out
                print(out)
                print(err)          
                result = p.returncode
                print("Result")
                print(result)
                msg = out2.decode("utf-8").split(":")[-1]
                reply = [msg.encode()]
                index +=1 
                p.kill()
            except subprocess.TimeoutExpired:
                reply = [definitions.W_ERROR]
                p.kill()
            
            # print(out2.decode("utf-8").split(":"))
            # print(out2.decode("utf-8")[0])
            # pattern = "*:msg:*"
            # results = re.match(pattern, out2.decode("utf-8"))
            # print(results)
            # threads[index] = threading.Thread(target=start_flowgraph, args=(flowgraph_vars, results, threads,index))
            # threads[index].start()


            # processes = []

            # pid = os.fork()
            # if pid == 0:
            #     start_flowgraph(flowgraph_vars, results, threads,index)
            # else:
            #     processes.append(pid)

           
            
            # reply = socket.recv()
            # print(reply)
            # if reply == definitions.W_REPLY:
            #     print("Recieved back from worker")
            #     # print(threading.get_native_id())
            #     # threads[index].join(10)
            #     # print(threads[index].is_alive())
            # else:
            #     print("Error")
            #     threads[index].terminate()
            # time.sleep(10)
            # print(results)
            # threads[index].kill()
            # index +=1
            #if there is a result send result back else send back an error code



if __name__ == '__main__':
    main()