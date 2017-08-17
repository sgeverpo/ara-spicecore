import serial
import time

commands = []

with open('settings.txt') as file:
    print "----- will be send: -----"
    for line in file:
        line = line.split(' ')
        if(line[0][0] == 'H'):
            break
        if not "sweep" in line:
            try:
                input = line[0].rstrip(')') + str(int(line[-1]))
                commands.append(input)
                print input
            except ValueError:
                try:
                    input = line[0].rstrip(')') + str(int(line[-2]))
                    commands.append(input)
                    print input
                except ValueError:
                    try:
                        input = line[0].rstrip(')') + str(float(line[-1]))
                        commands.append(input)
                        print input
                    except ValueError:
                        try:
                            input = line[0].rstrip(')') + str(float(line[-2]))
                            commands.append(input)
                            print input
                        except ValueError:
                            pass
    print "-------------------------"

ser = serial.Serial('/dev/ttyACM0', 9600)
if(not ser.isOpen()):
    raise ValueError("Could not open port.")
for command in commands:
    ser.write('C0' + command)
    print "Sent command: " + command
    out = ''
    time.sleep(0.005)
    while ser.inWaiting() > 0:
        out += ser.read(1)
    if out != '':
        print ">>" + out


