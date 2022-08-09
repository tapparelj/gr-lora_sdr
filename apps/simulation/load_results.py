from os import fork
import numpy as np
import matplotlib.pyplot as plt
import pickle

plt.figure()

folder = "results/"
file_list=["samp250000_bw125000_sf7_cr2_payLen32_cfo0_softTrue_ldroFalse.pkl","samp250000_bw125000_sf7_cr2_payLen32_cfo0_softFalse_ldroFalse.pkl"]
for file in file_list:
    snrs, FER, Glob_FER = pickle.load(open(folder+file,"rb"))
    plt.semilogy(snrs,Glob_FER,'-d',label=file)

plt.grid()
plt.xlabel('SNR [dB]')
plt.ylabel('Error rate')
plt.ylim([1e-4,1.05])
plt.legend(loc='upper right')
plt.show()
