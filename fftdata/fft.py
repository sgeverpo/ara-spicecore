#############################
#Code to take the Fast Fourier Transform of the data in this folder using the numpy fft functions.
#############################


import numpy as np
import matplotlib.pyplot as plt
import sys
import os

#try:
#    filename = sys.argv[1]
#except:
#    filename = raw_input("Give filename of data to FFT.\n>> ")
#namenumber = filename.split("_")[0]

for filename in os.listdir("/home/stef/stage/fftdata"):
    if filename.split(".")[-1] != "py" and filename.split("_")[0] != 'fft' and filename.split("_")[0] != 'timestamps':
        
    #    filename = namenumber + "_first_run"
        
        plt.subplot(2,1,1)
        t, Vt = np.loadtxt(filename,unpack=True)
        t = np.insert(t,0,0)
        Vt = np.insert(Vt,0,0)
    #    t = t[1775:2000]
    #    Vt= Vt[1775:2000]
        plt.plot(t,Vt,'-')
        plt.xlabel('t (s)')
        plt.ylabel('U (V)')
        
        freq = np.fft.rfftfreq(t.shape[-1],d=2.5e-10)
        Vf = np.fft.rfft(Vt)
        Vf = np.real(Vf)
#	Vf = np.square(Vf)
        
        plt.subplot(2,1,2)
        plt.plot(freq,Vf)
        plt.xlabel('f (Hz)')
        figname = "fft_" + filename + ".pdf"
        plt.savefig(figname,bbox_inches='tight')
        plt.close()
        
        outname = "fft_" + filename + ".txt" 
        outfile = open(outname,'w')
        for index, value in enumerate(Vf):
            outfile.write(str(freq[index]) + "\t" + str(value) + "\n")
        outfile.close()



#freq = np.fft.fftfreq(t.shape[-1])
#Vf = np.fft.fft(Vt)
#
#plt.plot(freq,Vf.real,freq,Vf.imag)
#plt.show()
