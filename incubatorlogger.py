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

splitted_line = line.split()

(uptime,
 tempSensor, tempTarget, tempPower, tempStatus,
 humidSensor, humidTarget, humidPower, humidStatus,
 turnerState, turnerActive, turnerTimeLeft, turnerStatus) = splitted_line[0:13]

if len(splitted_line) > 12:
    freeMemory = splitted_line[13]
else:
    freeMemory = None

points = [
        {
                "measurement": "uptime",
                "fields": {
                        "value": int(uptime)
                }
        },
        {
                "measurement": "temperature",
                "fields": {
                        "value": float(tempSensor),
                        "target": float(tempTarget),
                        "power": int(tempPower),
                        "status": bool(int(tempStatus))
                }
        },
        {
                "measurement": "humidity",
                "fields": {
                        "value": float(humidSensor),
                        "target": float(humidTarget),
                        "power": int(humidPower),
                        "status": bool(int(humidStatus))
                }
        },
        {
                "measurement": "turner",
                "fields": {
                        "state": bool(int(turnerState)),
                        "active": bool(int(turnerActive)),
                        "time_left": int(turnerTimeLeft),
                        "status": bool(int(turnerStatus))
                }
        }
]

if freeMemory is not None:
    points.append(
        {
                "measurement": "memory",
                "fields": {
                        "free": int(freeMemory)
                }
        }
    )

client.write_points(points)
