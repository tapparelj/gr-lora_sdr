#!/usr/bin/python

from subprocess import Popen, PIPE
import time
import os
import sys
import numpy as np


def append_to_name(x, suffix):
    x = x.split('.')
    return x[0] + suffix + '.' + x[1]

source = 'mu_tx_rx.py'
tmp_f = 'exp_su_per_tmp.py'

code = open(source).read()

snr = '/mu_snr.txt'
demod_s1 = '/mu_demod_s1.txt'
demod_s2 = '/mu_demod_s2.txt'
source_s1 = '/mu_source_s1.txt'
source_s2 = '/mu_source_s2.txt'
sync_state = '/sync_state.txt'

powers = 'power = [0,0]'
snr_thres = 'snr_thres = -9'
sto_param = 'sto = [0.0,0.0]'
rand_sto_param = 'rand_sto = [False,False]'
cfo_param = 'cfo = [0.0,0.0]'


for sto_run in [32.25]:
    STO = [0,sto_run]
    rand_sto = [False,False]
    CFO = [0,0.25]
    SIR = -3 # power u1-u2 only negative values are supported in multi user mode

    SNRs = range(-3,-17,-1)
    n_batches = 4
    batch_start = 0

    sf = 8
    bw = 250000.0

    n_frames = 5000
    interframe_symb = 400
    pay_len = 32

    folder = "exp_MU_sf{}_{}_{}_ku5_os8_pl{}_24-01-21".format(sf,STO[1],CFO[1],pay_len)


    est_duration = ((n_frames*(interframe_symb + 12.25 + pay_len)*2**sf/bw)*1.1+5)

    print "Estimated time: " ,est_duration*len(SNRs)*n_batches/60,"min"
    print "Param: CFO = ",CFO,", STO = ",STO

    time.sleep(2)
    for i in range(n_batches):
        for SNR in SNRs:
            print "SNR = ",SNR
        
            c = code
            c = c.replace(demod_s1, append_to_name(demod_s1, '_{}_{}'.format(SNR, i+batch_start)))
            c = c.replace(demod_s2, append_to_name(demod_s2, '_{}_{}'.format(SNR, i+batch_start)))

            c = c.replace(source_s1, append_to_name(source_s1, '_{}_{}'.format(SNR, i+batch_start)))
            c = c.replace(source_s2, append_to_name(source_s2, '_{}_{}'.format(SNR, i+batch_start)))

            c = c.replace(sync_state, append_to_name(sync_state, '_{}_{}'.format(SNR, i+batch_start)))

            c = c.replace(snr, append_to_name(snr, '_{}_{}'.format(SNR, i+batch_start)))

            c = c.replace(powers, "power = [{},{}]".format(SNR,SNR-SIR))

            c = c.replace(sto_param, "sto = [{},{}]".format(STO[0],STO[1]))
            c = c.replace(rand_sto_param, "rand_sto = [{},{}]".format(rand_sto[0],rand_sto[1]))
            c = c.replace(cfo_param, "cfo = [{},{}]".format(CFO[0],CFO[1]))

            if not os.path.exists('/home/jtappare/Documents/lora_gnu_radio_prototype/gr-lora_sdr/matlab/measurements/'+folder):
                os.makedirs('/home/jtappare/Documents/lora_gnu_radio_prototype/gr-lora_sdr/matlab/measurements/'+folder)
            elif SNR == SNRs[0] and i == 0:

                input=raw_input("Save folder \""+ folder+ "\" already exist. Is it fine to overwrite it? (y/N) ")
                if(input != "y"):
                    sys.exit()
            if SNR == SNRs[0] and i == 0: 
                f = open('/home/jtappare/Documents/lora_gnu_radio_prototype/gr-lora_sdr/matlab/measurements/'+folder+"/config.txt", "w")
                f.writelines("CFO:\t {}\n".format(CFO))
                f.write("STO:\t {} \n".format(STO))
                f.write("rand_sto:\t {} \n".format(rand_sto))
                f.write("SIR:\t {} \n".format(SIR))
                f.write("SNRs:\t {} \n".format(SNRs))
                f.write("sf:\t {} \n".format(sf))
                f.write("bw:\t {} \n".format(bw))
                f.write("n_frames:\t {} \n".format(n_frames))
                f.write("interframe_symb:\t {} \n".format(interframe_symb))
                f.write("pay_len:\t {} \n".format(pay_len))      

            c = c.replace("measurements", "measurements/"+folder)

            if SNR <= -8:
                c = c.replace(snr_thres, "snr_thres = {}".format(SNR-3))

            f = open(tmp_f, 'w')
            f.write(c)
            f.close()

            # real transmission
            p = Popen(['python '+tmp_f], stdin=PIPE, shell=True)
            time.sleep(est_duration)
            p.communicate(input='\n')

            # simulation
            # os.system('python '+tmp_f)

