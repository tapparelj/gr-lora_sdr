# Imports
from os import fork
import numpy as np
from flowgraph.tx_rx_simulation import tx_rx_simulation
import matplotlib.pyplot as plt
import string
import random 
import pickle
from threading import Thread
import threading
import time
#-----------------------------------------
#            Parameters Settings
#-----------------------------------------
sf = 7                  # Spreading factor
cr = 2                  # Coding rate
snrs = np.arange(-13,0,1) -3*(sf-7) # List of SNR to evaluate
n_frames = 100         # Number of frames transmitted per SNR
samp_rate = 500000      # Sample rate !Should be at least 4 time the bandwidth to avoid issue with the MMSE fractional resampler in the channel model!
bw = 125000             # LoRa bandwidth
center_freq = 868.1     # Center frequency in MHz
clk_offset_ppm = 0      # crystal offset in ppm
pay_len = 32            # in bytes
ldro = False            # usage of low datarate optimisation mode
soft_decoding = True   # usage of soft-decision decoding in hte receiver


# Result variables initialisation
FER = [0]*len(snrs) 
Glob_FER = [0]*len(snrs)  #paquet reception ratio

# Run experiments for one SNR
def run_exp(lock,snr_idx,tx_payload_file,rx_payload_file,rx_crc_file):
    SNRdB = snrs[snr_idx]
    print("Running SNR={}".format(SNRdB))
    simulator = tx_rx_simulation(tx_payload_file, rx_payload_file, rx_crc_file, impl_head=False, soft_decoding=soft_decoding, SNRdB=SNRdB, samp_rate=samp_rate, bw=bw,center_freq=center_freq, sf=sf, cr=cr, pay_len=pay_len, clk_offset_ppm=clk_offset_ppm, ldro=ldro)
    simulator.start()
    simulator.wait()
    #Get Frame error rate 
    
    lock.acquire()
    f = open(rx_crc_file)
    rx_crc = np.fromfile(f, dtype=np.uint8)
    if len(rx_crc) == 0:
        FER[snr_idx] = np.nan
        Glob_FER[snr_idx] = np.nan
    else:
        FER[snr_idx] = (1-sum(rx_crc)/len(rx_crc))
        Glob_FER[snr_idx] = (1-sum(rx_crc)/n_frames)
    f.close()
    lock.release()
    print("SNR {} done".format(SNRdB))

def main():
    start_time = time.time()    
    threads = []
    lock = threading.Lock()
    # For each SNR 
    for snr_idx in range(len(snrs)):
    
        #set temporary file names
        tx_payload_file = "./data/tx_payload{}.txt".format(snr_idx)
        rx_payload_file = "./data/rx_payload{}.txt".format(snr_idx)
        rx_crc_file     = "./data/rx_crc_valid{}.txt".format(snr_idx)

        #create Tx payload
        f = open(tx_payload_file, "w")
        letters = string.ascii_lowercase
        for i in range(n_frames):
            payload = ''.join(random.choice(letters) for i in range(pay_len)) 
            f.write(payload+",")
        f.close()

        # If you prefer not to use multiple threads, uncomment this line and comment the next three
        # run_exp(lock,snr_idx,tx_payload_file,rx_payload_file,rx_crc_file) 
        t = Thread(target=run_exp, args=(lock,snr_idx,tx_payload_file,rx_payload_file,rx_crc_file))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print("--- Simulation time: %s seconds ---" % (time.time() - start_time))
    
    #-----------------------------------------
    #                Plot results
    #-----------------------------------------
    plt.figure()
    plt.semilogy(snrs,FER,'-d',label='FER')
    plt.semilogy(snrs,Glob_FER,'-d',label='FER including frame miss')
   
    plt.xlabel('SNR [dB]')
    plt.ylabel('Error rate')
    plt.ylim([10/n_frames,1.05])
    plt.xlim([min(snrs),max(snrs)])
    plt.grid('minor')
    plt.legend(loc='upper right')
    # Save results
    curve_name = "samp{}_bw{}_sf{}_cr{}_payLen{}_clk_offset_ppm{}_soft{}_ldro{}".format(samp_rate, bw, sf, cr, pay_len, clk_offset_ppm ,soft_decoding, ldro)
    plt.savefig("results/"+curve_name+".png")
    with open('results/'+curve_name+'.pkl', 'wb') as f:
        pickle.dump([snrs, FER, Glob_FER],f)
    plt.show()


if __name__ == "__main__":
    main()
