#!/usr/bin/env python

import serial
import sys
import datetime as dt
import time

ser = serial.Serial('/dev/ttyACM0', 115200)
logfile = open('/tmp/incubatorlog.txt','a')

ser.write('G')
while ser.inWaiting() == 0:
	ser.write('G')
        time.sleep(1)

line = ser.readline()
logfile.write(str(dt.datetime.now()) + ' ')
logfile.write(line)
logfile.close()
