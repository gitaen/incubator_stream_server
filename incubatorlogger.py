#!/usr/bin/env python3

import serial
from influxdb import InfluxDBClient
import time

ser = serial.Serial('/dev/ttyACM0', 115200)
client = InfluxDBClient(database='incubator')

ser.write('G'.encode())
while ser.inWaiting() == 0:
        ser.write('G'.encode())
        time.sleep(1)

line = ser.readline()

(uptime,
 tempSensor, tempTarget, tempPower, tempStatus,
 humidSensor, humidTarget, humidPower, humidStatus,
 turnerState, turnerActive, turnerTimeLeft, turnerStatus) = line.split()

points = [
        {
                "measurement" : "uptime",
                "fields" : {
                        "value" : int(uptime)
                }
        },
        {
                "measurement" : "temperature",
                "fields" : {
                        "value" : float(tempSensor),
                        "target" : float(tempTarget),
                        "power" : int(tempPower),
                        "status" : bool(tempStatus)
                }
        },
        {
                "measurement" : "humidity",
                "fields" : {
                        "value" : float(humidSensor),
                        "target" : float(humidTarget),
                        "power" : int(humidPower),
                        "status" : bool(humidStatus)
                }
        },
        {
                "measurement" : "turner",
                "fields" : {
                        "state" : bool(turnerState),
                        "active" : bool(turnerActive),
                        "time_left" : int(turnerTimeLeft),
                        "status" : bool(turnerStatus)
                }
        }
]

client.write_points(points)
