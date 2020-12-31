#!/bin/bash

# Start the run once job.
echo "Docker container has been started"

# Setup a cron schedule
echo "* * * * * /usr/bin/python /rpi-cpu2mqtt.py
# This extra line makes it a valid cron" > scheduler.txt

crontab scheduler.txt
cron -f