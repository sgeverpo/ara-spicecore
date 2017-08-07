#############################################
#This code generates a series of pulses using the Windfreak SynthNV RF signal generator.
#The format is as follows: Send "amount_pulse" of pulses of frequency 1 with a waiting time "period" between them.
#Wait for a time interval "pause" before going to the next frequency. Repeat for all frequencies given in "frequencies".
#"frequencies", "amount_pulse", "period" and "pause" are read from an input file as specified by the initialize(filename) function.
#############################################


import time
import serial
import thread

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
                period = int(line.strip())*0.001
            if i == 3:
                pause = int(line.strip())*0.001
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
    for freq in frequencies:
        writeToSynth("f"+freq,serial)
        for i in range(amount_pulse):
            sendPulse(serial)
#            try:
#                thread.start_new_thread(readSynth, (serial, ))
#            except:
#                print "Error: could not start read-thread."
            time.sleep(period)
        time.sleep(pause)

def stop(ser):
    while 1:
        input = raw_input("Type 'exit' to stop: ")
        if(input == "exit"):
            ser.close()
            thread.interrupt_main()
            exit()
        
#Execution of the functions that making up the code.
#Initialize the program from input.txt.
frequencies, amount_pulse, period, pause = initialize("input.txt")

#Open the serial port where the Windfreak SynthNV signal generator is connected. 
ser = serial.Serial('/dev/tty.usbmodem12341', 9600)

#Run the main part of the code.
#try:
#    thread.start_new_thread(stop, (ser, ))
#except:
#    print "Error: could not start close-thread."
main_loop(frequencies,amount_pulse,period,pause,ser)

#When finished, close the serial port.
ser.close()
