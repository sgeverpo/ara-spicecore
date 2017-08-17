#this script is an example of how to write files to the SD card and of how to write the time
#(time should be updated on boot from the RTC)
#(microSD should be mounted to /media/card, this happens automatically when it is inserted before starting the BBB. For more info on mounting / unmounting see our manual)

import datetime

logfile = open("/media/card/test.txt",'w')

for i in range(100):
    logfile.write(str(datetime.datetime.now().time()) + '\n')


logfile.close()
