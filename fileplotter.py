#!/usr/bin/env python

import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot
import sys
import time
import datetime as dt

xPoints = []
yPoints = []
for i in range(len(sys.argv)-3):
	yPoints.append([])

temp = []
temp_target = []

for line in sys.stdin:
    reading = line.split()

    xPoints.append(dt.datetime.strptime(' '.join(reading[0:2]), '%Y-%m-%d %H:%M:%S.%f'))
#    temp.append(float(reading[3]))
#    temp_target.append(float(reading[4]))
    for i in range(len(sys.argv)-3):
	yPoints[i].append(float(reading[int(sys.argv[i+3])-1]))

pyplot.suptitle(sys.argv[2]);
pyplot.xticks(rotation='vertical')
pyplot.subplots_adjust(bottom=.3)
for i in yPoints:
	pyplot.plot(xPoints, i);	
pyplot.savefig(sys.argv[1])
pyplot.close()
