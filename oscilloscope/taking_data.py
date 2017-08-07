#!/usr/bin/env python

########################
# This program takes data from the oscilloscope MSO6104A. The data is stored in the directory 'data',
# which you should make yourself (in the same location as this .py file). 
# It uses the file 'LinacRunNumber' to assign a number to the overall run.
# Just connect both the computer and the oscilloscope to a local network, or connect the two using LAN, and start running the program when connection is established.
# Add a label when running the program, e.g. type in the terminal "python taking_data.py my_measurement" to start the measurement.
# Adjust some settings in the code if needed, e.g. the voltage-range in which the oscilloscope will take measurements.
# When a timeout occures, the program fires up a bunch of errors instead of terminating properly. Just pushing the run/stop button on the oscilloscope couple of times should enable you to run the program again for further measurements if needed.
########################

import time, csv, string, sys, os

import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as ppl

import visa
rm = visa.ResourceManager()

print (rm.list_resources())
agilent = rm.open_resource("TCPIP0::172.17.10.147::inst0::INSTR")
print(agilent.query("*IDN?"))

agilent.timeout = 30000 # 30 s in ms
try:
    #
    label=sys.argv[1]
    
    # This array gives the full voltage range (in volts) wherein the oscilloscope will make its measurements. The first element corrsponds to channel 1, the second to channel 2 etc.
    changains = [8,3.2,3.2,8.0]

    agilent.write("*CLS")
    agilent.write("*RST")
    
    # The channel which will be used.
    agilent.write(":VIEW CHAN1")

    # The time-scale (= the horizontal length of 1 block on the screen of the oscilloscope) in seconds. The total range is 10*scale.
    scale = "10E-9"
    agilent.write(":TIMEBASE:SCALE " + scale)
    
    # The time-delay. This moves the signal to the right on the screen of the oscilloscope if the value is positive.
    delay = "235E-9"
    agilent.write(":TIMEBASE:DELAY " + delay)
    agilent.write(":TIMEBASE:REFERENCE CENTER")

    # Some additional settings. Should be OK.
    agilent.write(":TRIGGER:MODE EDGE")
    agilent.write(":TRIGGER:SWEEP TRIG")
    agilent.write(":TRIGGER:EDGE:SOURCE CHAN1")
    agilent.write(":TRIGGER:EDGE:SLOPE POSITIVE")

    agilent.write(":CHANNEL1:RANGE %f" % changains[0])
    agilent.write(":TRIGGER:LEVEL CHAN1,0.015")
    # Setting the input impedance. Should be fifty for the callibration pulses for the ice.
    agilent.write(":CHANNEL1:IMPEDANCE FIFTY")

    #agilent.write(":CHANNEL2:RANGE %f" % changains[1])
    #agilent.write(":TRIGGER:LEVEL CHAN2,-0.04")
    #
    #agilent.write(":CHANNEL3:RANGE %f" % changains[2])
    #agilent.write(":TRIGGER:LEVEL CHAN3,-0.04")
    #
    #agilent.write(":CHANNEL4:RANGE %f" % changains[3])
    #agilent.write(":TRIGGER:LEVEL CHAN4, 0.015")

    #converter=u's'   for ascii query

    # Sets the number of datapoints taken. 
    agilent.write(":WAVeform:POINts:MODE MAXIMUM")
    agilent.write(":WAVeform:POINts <maximum # points>")

    #agilent.write(":SYSTEM:HEADER OFF")
    agilent.write(":ACQUIRE:MODE RTIME")
    agilent.write(":WAVEFORM:FORMAT ASCII")

    # The number of times the oscilloscope will wait for a trigger.
    nruns = 240
    start = time.clock()

    filename_root="data/linac"

    try:
        runfile = open("LinacRunNumber", "r")
    except:
        runfile = open("LinacRunNumber", "w")
        runfile.write("0")
        runfile.close()
        runfile = open("LinacRunNumber", "r")
        
    runnum = runfile.readline()
    runnum.rstrip('\n')
    runfile.close()

    new_runnum = [str(int(runnum)+1)]
    runfile = open("LinacRunNumber", "w")
    runfile.writelines(new_runnum)
    runfile.close()

    print "================================="
    print "BEGINNING RUN", runnum
    print "================================="

    filename = "data/timestamps_%s" % (runnum)
    timefile = open(filename, "w")

    for run in range(nruns):
        
        ## Measuring the frequency and peak-to-peak value.
        #freq = agilent.query_ascii_values(":MEASure:FREQuency?")[0]
        #ptp = agilent.query_ascii_values(":MEASure:VPP?")[0]
            
        time1 = time.clock()
        now_time = time.localtime()
        
        agilent.write(":DIGITIZE")
        
        agilent.write(":WAVEFORM:SOURCE CHANNEL1")
        
        # The voltage-values of the measurement.
        values = agilent.query_ascii_values(":WAVEFORM:DATA?", converter='s') #has /n at end
        
        # Fixing the weird layout of the first voltage.
        try:
            values[0] = values[0].split()[1]
        except:
            try:
                splitted = values[0].split('-')
                values[0] = "-" + splitted[1] + "-" + splitted[2]
            except:
                splitted = values[0].split('-')
                values[0] = "-" + splitted[1]
        
        # The time-values.
        xOrg = agilent.query_ascii_values(":WAVeform:XORigin?")[0]
        xInc = agilent.query_ascii_values(":WAVeform:XINCrement?")[0]
        lTime = -5*float(scale)
        start = round((lTime - xOrg)/xInc)
        times = []
        for i in range(0, len(values)):
            times.append((start + i)*xInc + xOrg)

        # Writing to file.
        print "Data acquired!"
        filename = filename_root + "1_%i_%s_%s" % (run, label, runnum)
        f = open(filename, "w")
        f.write("%s\n%s\n" % (freq, ptp))
        for i in range(0, len(values)):
            f.write("%s\t%s\n" % (times[i], values[i]))        
        f.close()
        
        '''
        agilent.write(":WAVEFORM:SOURCE CHANNEL2")
        values = agilent.query_ascii_values(":WAVEFORM:DATA?",converter='s') #has /n at end
        
        filename = filename_root + "2_%i_%s_%s" % (run, label, runnum)
        f = open(filename, "w")
        for value in values:
            f.write("%s\n" % value)
        f.close()

        agilent.write(":WAVEFORM:SOURCE CHANNEL3")
        values = agilent.query_ascii_values(":WAVEFORM:DATA?",converter='s') #has /n at end
        
        filename = filename_root + "3_%i_%s_%s" % (run, label, runnum)
        f = open(filename, "w")
        for value in values:
            f.write("%s\n" % value)
        f.close()

        agilent.write(":WAVEFORM:SOURCE CHANNEL4")
        values = agilent.query_ascii_values(":WAVEFORM:DATA?",converter='s') #has /n at end
        
        filename = filename_root + "4_%i_%s_%s" % (run, label, runnum)
        f = open(filename, "w")
        for value in values:
            f.write("%s\n" % value)
        f.close()
            '''
            
        timefile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (run,time1,now_time[0],now_time[1],now_time[2],now_time[3],now_time[4],now_time[5])) #year, month, day, hour, minute, second

        time2 = time.clock()
        print "Shot ", run,": ", time2-time1, " s"

    timefile.close()
    agilent.write("SYSTEM:LOCK 0")
    agilent.close()

    print "================================="
    print "ENDING RUN", runnum
    print "================================="


    elapsed = time.clock() - start
    print "Total time: ", elapsed
    print "Time per shot: ", elapsed/float(nruns), " s"
    
except:
    print "Timeout!"
    agilent.write("SYSTEM:LOCK 0")
    agilent.close()

