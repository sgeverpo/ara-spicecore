#!/usr/bin/python
#############################################
#This code generates a series of pulses using the Windfreak SynthNV RF signal generator.
#The format is as follows: Send "amount_pulse" of pulses of frequency 1 with a waiting time "period" between them.
#Wait for a time interval "pause" before going to the next frequency. Repeat for all frequencies given in "frequencies".
#"frequencies", "amount_pulse", "period" and "pause" are read from an input file as specified by the initialize(filename) function.
#
#This code also logs certain quantities.
#When changing frequencies, a pulse of 1ms is sent which is used to read back the power coming into the RFin input of the SynthNV
#After every pulse the pressure is logged (measured with the ADC pins) as well as the time.
#In the waiting time between changing frequencies, an attempt is made to read the temperature from the sensor.
#############################################


import os
import time
import serial
from threading import Thread
import Adafruit_BBIO.ADC as ADC
import datetime
import Adafruit_DHT


def initialize(filename):
    '''Read input from a file given as argument. The file should have the frequencies at which to send pulses in MHz at its first (not comment) line, separated by spaces. The second line has the amount of pulses to send at each frequency. The third line has the time between pulses in milliseconds. The fourth line has the pause between sending pulses of certain frequencies in ms.'''
    f = open(filename,'r')
    
    i = 0
    for line in f:
        if line[0] != "#":
            if i == 0:
                frequencies = [freq.strip() for freq in line.split(" ")]
            if i == 1:
                amount_pulse = int(line.strip())
            if i == 2:
                period = float(line.strip())*0.001
            if i == 3:
                pause = float(line.strip())*0.001
            i += 1
            
    return frequencies, amount_pulse, period, pause

def writeToSynth(message,serial):
    '''Write commands to the Windfreak SynthNV RF signal generator through the serial port. The C0 writes to channel 0 of the SynthNV.'''
    serial.write("C0"+message)

def readSynth(serial):
    '''Read output from the signal generator through the serial port. As long as there is stuff in the buffer, read it out byte by byte.'''
    while serial.inWaiting() > 0:
        serial.read(1)

def sendPulse(serial):
    '''Give the command to the signal generator to send one pulse.'''
    writeToSynth("G", serial)

def readPressure():
    #Read the pressure sensor from one of the analog pins
    #In current, 92.4 is the resistor value in Ohms
    voltage = ADC.read("P9_38") * 1.8
    current = voltage / 92.4
    return current

def logTemperature(logfile):
    humidity, temperature = Adafruit_DHT.read_retry(sensor,pin,2,2)
    result = temperature if temperature is not None else "Failed"
    logfile.write("Temperature (Celsius) = %s\n" % result)

def logPulse(logfile):
    current = readPressure()            
    logfile.write("Sent pulse @ time =  %s,  pressure output (mA) =  %s\n" % (datetime.datetime.now().time(),current))

    
def main_loop(frequencies,amount_pulse,period,pause,serial,logfile):
    '''Execute the transmission of the pulses. This function will send the given amount of pulses at each frequency with the specified interval between them and with the given pause between series of pulses at different frequencies. To clear the generator's output from the buffer, it is read out in a thread running during the waiting time between pulses.'''
    power_results = []
    logfile.write("####Start loop####\n")
    for freq in frequencies:
        writeToSynth("f"+freq,serial)
        logfile.write("\nSet frequency at %sMHz\n\n" % freq)

        #send continuous pulse to read back power
        writeToSynth('a12',serial)
        currentTime = time.time()
        sendTime = 0.001 #how long to send continuous pulse (in s)
        while time.time() <=  currentTime + sendTime:
            writeToSynth('w',serial)
        writeToSynth('G',serial)    
            
        currentTime = time.time()
        out = ''
        while time.time() < currentTime + period:
            if serial.inWaiting() > 0:
                while serial.inWaiting() > 0:
                    out += serial.read(1)
        power_results.append(out)
        
        logfile.write("Power readings (dBm): \n")
        for item in power_results:
            split = item.split("\n")
            for value in split:
                if "." in value:
                    logfile.write(str(value) + '\n')
        logfile.write("\n")

        #send the normal pulses
        for i in range(amount_pulse):
            sendPulse(serial)
            
            logThread = Thread(target = logPulse, args=(logfile,))
            logThread.start()

            time.sleep(period)
            
            #using a while loop and the time function seems to give more accurate waiting times
            #currentTime = time.time()
            #while time.time() < currentTime + period:
            #    pass            
        logfile.write('\n')
        #start thread in which temperature is measured and logged during the pause between frequencies
        tempThread = Thread(target = logTemperature, args=(logfile,))
        tempThread.start()
        time.sleep(pause)
    logfile.write("\n####End loop.####\n\n")
    return power_results
        
#Execution of the functions that making up the code.

#give the BBB some time to mount the microSD and set the clock after booting
os.system("mount /dev/mmcblk0p1 /media/card") # happens automatically at boot but added this just to be sure...
time.sleep(10)

#Initialize the program from input.txt.
frequencies, amount_pulse, period, pause = initialize("input.txt")

#Initialize the analog pin to read the pressure sensor
ADC.setup()

#Open the serial port where the Windfreak SynthNV signal generator is connected. 
ser = serial.Serial('/dev/ttyACM0', 9600)

#variables for temperature sensor: sensor is the used model, pin is the GPIO pin connected to the DHT22 data pin
sensor = Adafruit_DHT.DHT22
pin = 'P8_11'

current = readPressure()

#Run the main part of the code.
logfilename = "log_a12_new.txt"
logfile = open("/media/card/" + logfilename,'w')
logfile.write("########START########\n")
logfile.write("Time = %s\n" %datetime.datetime.now().time())
logfile.write("Pressure output (mA) = %s\n" %current)
logfile.close()

writeToSynth("o1",ser)

#THIS SHOULD LOOP INFINITELY ON THE POLE SO SMALL CHANGES ARE NECESSARY AFTER TESTING
loopcount = 1
while loopcount <= 1:
    logfile = open("/media/card/" + logfilename,'a')    
    print "\nStart loop %s" % loopcount
    power_results = main_loop(frequencies,amount_pulse,period,pause,ser,logfile)
    logfile.close()
    os.system("umount -l /dev/mmcblk0p1")
    os.system("mount /dev/mmcblk0p1 /media/card")
    loopcount += 1


current = readPressure()
logfile = open("/media/card/" + logfilename,'a')
logfile.write("########FINISHED.########\n")
logfile.write("Time = %s\n" %datetime.datetime.now().time())
logfile.write("Pressure output (mA) = %s\n" %current)
time.sleep(1) #to give the final temperature measurement enough time for 2 tries
logfile.close()

os.system("umount -l /dev/mmcblk0p1")

#When finished, close the serial port.
ser.close()

