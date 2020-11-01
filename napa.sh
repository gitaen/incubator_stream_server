#!/bin/sh

while true; do
    tail -n 1 /tmp/incubatorlog.txt | /home/pi/src/incubator/turningdate.py > /var/run/ffmpeg/remaining_new.txt;
    mv /var/run/ffmpeg/remaining_new.txt /var/run/ffmpeg/remaining.txt;
done
