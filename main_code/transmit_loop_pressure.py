#############################################
#This code generates a series of pulses using the Windfreak SynthNV RF signal generator.
#The format is as follows: Send "amount_pulse" of pulses of frequency 1 with a waiting time "period" between them.
#Wait for a time interval "pause" before going to the next frequency. Repeat for all frequencies given in "frequencies".
#"frequencies", "amount_pulse", "period" and "pause" are read from an input file as specified by the initialize(filename) function.
#
#This version sends a long burst for each frequency to read back the power and will also make a pressure measurement
#when running the code. These results are written to a textfile.
#############################################


import time
import serial
import thread
import Adafruit_BBIO.ADC as ADC

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
    
def main_loop(frequencies,amount_pulse,period,pause,serial):
    '''Execute the transmission of the pulses. This function will send the given amount of pulses at each frequency with the specified interval between them and with the given pause between series of pulses at different frequencies. To clear the generator's output from the buffer, it is read out in a thread running during the waiting time between pulses.'''
    print "Start"
    power_results = []
    for freq in frequencies:
        writeToSynth("f"+freq,serial)
        
        #send continuous pulse to read back power
        writeToSynth('a2',serial)
        currentTime = time.time()
        sendTime = 0.001 #how long to send continuous pulse (in s)
        while time.time() <=  currentTime + sendTime:
            writeToSynth('w',serial)
        writeToSynth('G',serial)    
            
        power_results.append("#frequency %s" %(freq))
        currentTime = time.time()
        out = ''
        while time.time() < currentTime + period:
            if serial.inWaiting() > 0:
                while serial.inWaiting() > 0:
                    out += serial.read(1)
        power_results.append(out)


        #send the normal pulses
        for i in range(amount_pulse):
            sendPulse(serial)
            #try:
            #    thread.start_new_thread(readSynth, (serial, ))
            #except:
            #    print "Error: could not start read-thread."
            time.sleep(period)

            #using a while loop and the time function seems to give more accurate waiting times
            #currentTime = time.time()
            #while time.time() < currentTime + period:
            #    pass            

        time.sleep(pause)
    print "Finished."
    return power_results
#def stop(ser):
#    while 1:
#        input = raw_input("Type 'exit' to stop: ")
#        if(input == "exit"):
#            ser.close()
#            thread.interrupt_main()
#            exit()
        
#Execution of the functions that making up the code.
#Initialize the program from input.txt.
frequencies, amount_pulse, period, pause = initialize("input.txt")

#Initialize the analog pin to read the pressure sensor
ADC.setup()

#Open the serial port where the Windfreak SynthNV signal generator is connected. 
ser = serial.Serial('/dev/ttyACM0', 9600)


#try:
#    thread.start_new_thread(stop, (ser, ))
#except:
#    print "Error: could not start close-thread."

#Read the pressure sensor from one of the analog pins
voltage = ADC.read("P9_38") * 1.8
current = voltage / 92.4

#Run the main part of the code.
power_results = main_loop(frequencies,amount_pulse,period,pause,ser)

#When finished, close the serial port.
ser.close()

outfile = open("output_test.txt",'w')
outfile.write("#Pressure sensor output: %s A\n" %(current))
outfile.write("#Power readings: \n")
for item in power_results:
    split = item.split("\n")
    for value in split:
        if "." in value or "#" in value:
            outfile.write(str(value) + '\n')
outfile.close()

