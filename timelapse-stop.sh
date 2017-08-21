#!/bin/bash

# Kill a running timelapse.
kill $(ps aux | grep '/[u]sr/bin/python /home/pi/pi-timelapse/timelapse.py' | awk '{print $2}')
