# Imports
from os import fork
import numpy as np
import tx_rx_simulation
import matplotlib.pyplot as plt
import string
import random 
import pickle
from threading import Thread
import threading

# Setting parameters
sf = 7
cr = 2
snrs = [10] #np.arange(-12.5,0,1.5) -3*(sf-7)
n_frames = 3
samp_rate = 500000
bw = 125000
center_freq = 868.1 #in MHz
clk_offset_ppm = 20 #crystal offset in ppm

cfo = center_freq*clk_offset_ppm*2**sf/samp_rate
print("CFO = {}".format(cfo))

sfo = 0
pay_len = 32
ldro = False
soft_decoding = True


# Variable initialisation
FER = [0]*len(snrs) 
Glob_FER = [0]*len(snrs)  #paquet reception ratio

def run_exp(lock,snr_idx,tx_payload_file,rx_payload_file,rx_crc_file):
    SNRdB = snrs[snr_idx]
    print("Running SNR={}".format(SNRdB))
    simulator = tx_rx_simulation.tx_rx_simulation(tx_payload_file, rx_payload_file, rx_crc_file, impl_head=False, soft_decoding=soft_decoding, SNRdB=SNRdB, samp_rate=samp_rate, bw=bw, sf=sf, cr=cr, pay_len=pay_len, CFO=cfo, SFO=sfo, ldro=ldro)
    simulator.start()
    simulator.wait()
    #Get Frame error rate 
    
    lock.acquire()
    rx_crc = np.fromfile(open(rx_crc_file), dtype=np.uint8)
    if len(rx_crc) == 0:
        FER[snr_idx] = np.nan
        Glob_FER[snr_idx] = np.nan
    else:
        FER[snr_idx] = (1-sum(rx_crc)/len(rx_crc))
        Glob_FER[snr_idx] = (1-sum(rx_crc)/n_frames)
    lock.release()
    print("SNR {} done".format(SNRdB))

def main():
    
    threads = []
    lock = threading.Lock()
    # For each SNR 
    for snr_idx in range(len(snrs)):
    
        #setup variables
        tx_payload_file = "./simulation/data/tx_payload{}.txt".format(snr_idx)
        rx_payload_file = "./simulation/data/rx_payload{}.txt".format(snr_idx)
        rx_crc_file     = "./simulation/data/rx_crc_valid{}.txt".format(snr_idx)

        #create Tx payload
        f = open(tx_payload_file, "w")
        letters = string.ascii_lowercase
        for i in range(n_frames):
            payload = ''.join(random.choice(letters) for i in range(pay_len)) 
            f.write(payload+",")
            # f.write("kewnppwhiiepxpgwganiedllpycxtxnr,")
        f.close()
        
        t = Thread(target=run_exp, args=(lock,snr_idx,tx_payload_file,rx_payload_file,rx_crc_file))
        threads.append(t)
        t.start()

        # run_exp(lock,snr_idx,tx_payload_file,rx_payload_file,rx_crc_file)
    for t in threads:
        t.join()
    
    plt.figure()
    plt.semilogy(snrs,FER,'-d',label='FER')
    plt.semilogy(snrs,Glob_FER,'-d',label='FER including frame miss')
    plt.grid()
    plt.xlabel('SNR [dB]')
    plt.ylabel('Error rate')
    plt.ylim([1e-4,1.05])
    plt.xlim([min(snrs),max(snrs)])
    plt.legend(loc='upper right')

    curve_name = "samp{}_bw{}_sf{}_cr{}_payLen{}_cfo{}_sfo{}_soft{}_ldro{}".format(samp_rate, bw, sf, cr, pay_len, cfo, sfo ,soft_decoding, ldro)
    plt.savefig("simulation/results/"+curve_name+".png")
    with open('simulation/results/'+curve_name+'.pkl', 'wb') as f:
        pickle.dump([snrs, FER, Glob_FER],f)
    plt.show()


if __name__ == "__main__":
    main()
