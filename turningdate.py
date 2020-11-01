#!/usr/bin/env python
from __future__ import print_function
import sys
from time import sleep
import datetime as dt

temp = []
temp_target = []

for line in sys.stdin:
    reading = line.split()

    logDate = dt.datetime.strptime(' '.join(reading[0:2]), '%Y-%m-%d %H:%M:%S.%f')
#    logDate = dt.datetime.strptime(' '.join(reading[0:2]), '%Y-%m-%d %H:%M:%S')
    logRemaining = dt.timedelta(0, int(reading[13]))
    turnDate = logDate + logRemaining
#    print(turnDate)
#    print(now)
    remaining = turnDate.replace(microsecond=0) - dt.datetime.now().replace(microsecond=0)
    print("Turning in {}".format(remaining), end='')
    sleep(0.5)
