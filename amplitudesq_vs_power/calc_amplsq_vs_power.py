####################
# This program adds the files 'amplitude.txt' and 'power.txt' together to form 'amplsq_vs_power.txt'.
# This last file contains a column with the measured amplitudes squared and a column with the measured power.
# amplitude.txt contains the amplitudes (manually) measured using the oscilloscope, power.txt contains the corresponding powers measured by the Windfreak SynthNV.
####################

import numpy as np

ampl = np.loadtxt("amplitude.txt")
power = np.loadtxt("power.txt")
calc = []

for elt in power:
    calc.append(10**(elt/10))
    
file = open("amplsq_vs_power.txt", 'w')
for i in range(len(calc)):
    file.write("%s\t%s\n" % (ampl[i]**2, calc[i]))
file.close()
