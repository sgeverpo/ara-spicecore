#############################################
#This code can be used for easy serial communication with hardware connected over USB
#Give the command, press enter and output will be print
#############################################
import time
import serial

#added for the Windfreak SynthNV so this doesn't have to be typed every command
channel = "C0"

#open the serial connection with the device
ser = serial.Serial('/dev/ttyACM0', 9600)

ser.isOpen()

print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

input=1
while 1 :
    # get keyboard input
    input = raw_input(">> ")
        # Python 3 users
        # input = input(">> ")
    if input == 'exit':
        ser.close()
        exit()
    else:
        # send the character to the device
        ser.write(channel + input)
        out = ''
        # give the device some time to answer
        time.sleep(0.01)
        while ser.inWaiting() > 0:
            out += ser.read(1)
        if out != '':
            print ">>" + out
