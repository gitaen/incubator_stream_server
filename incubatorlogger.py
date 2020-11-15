#!/usr/bin/env python3

import serial
from pymongo import MongoClient
from datetime import datetime
import time

ser = serial.Serial('/dev/ttyACM0', 115200)
client = MongoClient()
db = client.incubator
collection = db.log

ser.write('G')
while ser.inWaiting() == 0:
	ser.write('G')
        time.sleep(1)

line = ser.readline()

(uptime,
 tempSensor, tempTarget, tempPower, tempStatus,
 humidSensor, humidTarget, humidPower, humidstatus,
 turnerState, turnerActive, turnerTimeLeft, turnerStatus) = line.split()

logLine = {"TimeStamp" : datetime.datetime.utcnow(),
           "Uptime" : int(uptime),
           "Temperature" : { "Current" : float(tempSensor),
                             "Target" : float(tempTarget),
                             "Power" : int(tempPower),
                             "StatusOK" : bool(tempStatus)},
           "Humidity" : { "Current" : float(humidSensor),
                          "Target" : float(humidTarget),
                          "Power" : int(humidPower),
                          "StatusOK" : bool(humidStatus)},
           "Turner" : { "State" : bool(turnerState),
                        "Active" : bool(turnerActive),
                        "TimeLeft" : int(TurnetTimeLeft),
                        "StatusOK" : bool(turnetStatus)}
           }

collection.insert_one(logLine)
