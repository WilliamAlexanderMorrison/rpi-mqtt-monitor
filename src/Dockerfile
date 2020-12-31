FROM debian:stretch

# Install cron
RUN apt-get update && apt-get install -y \
        cron \
        python-pip

RUN pip install paho-mqtt \
        psutil

# Add files
ADD rpi-cpu2mqtt.py /rpi-cpu2mqtt.py
ADD config.py /config.py
ADD entrypoint.sh /entrypoint.sh

RUN chmod +x /rpi-cpu2mqtt.py /config.py /entrypoint.sh

ENTRYPOINT /entrypoint.sh