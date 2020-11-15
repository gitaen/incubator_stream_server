#!/usr/bin/env python3

import serial
from pymongo import MongoClient
from datetime import datetime
import time

ser = serial.Serial('/dev/ttyACM0', 115200)
client = MongoClient()
db = client.incubator
collection = db.log

ser.write('G'.encode())
while ser.inWaiting() == 0:
        ser.write('G'.encode())
        time.sleep(1)

line = ser.readline()

(uptime,
 tempSensor, tempTarget, tempPower, tempStatus,
 humidSensor, humidTarget, humidPower, humidStatus,
 turnerState, turnerActive, turnerTimeLeft, turnerStatus) = line.split()

logLine = {"TimeStamp" : datetime.utcnow(),
           "Uptime" : int(uptime),
           "Temperature" : { "Measurement" : float(tempSensor),
                             "Target" : float(tempTarget),
                             "Power" : int(tempPower),
                             "StatusOK" : bool(tempStatus)},
           "Humidity" : { "Measurement" : float(humidSensor),
                          "Target" : float(humidTarget),
                          "Power" : int(humidPower),
                          "StatusOK" : bool(humidStatus)},
           "Turner" : { "State" : bool(turnerState),
                        "Active" : bool(turnerActive),
                        "TimeLeft" : int(turnerTimeLeft),
                        "StatusOK" : bool(turnerStatus)}
           }

collection.insert_one(logLine)
