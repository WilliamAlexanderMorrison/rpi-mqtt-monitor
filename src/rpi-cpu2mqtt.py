# Python (runs on 2 and 3) script to check cpu load, cpu temperature and free space,
# on a Raspberry Pi computer and publish the data to a MQTT server.
# RUN pip install paho-mqtt
# RUN sudo apt-get install python-pip

from __future__ import division
import subprocess, time, socket, os
import paho.mqtt.client as paho
import json
import config

import psutil

# get device host name - used in mqtt topic
hostname = socket.gethostname()


def check_used_space(path):
                #https://stackoverflow.com/questions/12027237/selecting-specific-columns-from-df-h-output-in-python
                try:
                    p = subprocess.Popen("df -Ph", stdout=subprocess.PIPE, shell=True)
                    dfdata, _ = p.communicate()
                except:
                    return False

                dfdata = dfdata.splitlines()
                used_space = dfdata[1].split()
                return used_space[4].rstrip("%")

def check_cpu_load():
                #https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/components/systemmonitor/sensor.py
                try:
                    result = round(os.getloadavg()[0], 2)
                except:
                    return False

                return result

def check_voltage():
                full_cmd = "vcgencmd measure_volts | cut -f2 -d= | sed 's/000//'"
                voltage = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
                voltage = voltage.strip()[:-1]
                return voltage

def check_swap():
                full_cmd = "free -t | awk 'NR == 3 {print $3/$2*100}'"
                swap = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
                swap = round(float(swap), 1)
                return swap

def check_memory():
                try:
                    memory = psutil.virtual_memory().percent
                except:
                    return False

                return memory


def check_cpu_temp():
                #https://thesmithfam.org/blog/2005/11/19/python-uptime-script/
                try:
                    f = open( "/sys/class/thermal/thermal_zone0/temp" )
                    cpu_temp = f.read().split()
                    f.close()
                except:
                    return False

                return cpu_temp[0]

def check_sys_clock_speed():
                full_cmd = "awk '{printf (\"%0.0f\",$1/1000); }' </sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
                return subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

def check_uptime():
                try:
                    result = psutil.boot_time()
                except:
                    return False

                return result

def check_power_supply():
                #https://github.com/custom-components/sensor.rpi_power/blob/master/custom_components/rpi_power/sensor.py
                try:
                    f = open( "/sys/devices/platform/soc/soc:firmware/get_throttled" )
                    contents = f.read().split()
                    f.close()
                except:
                    return False

                if contents[0] == '0':
                    result = 'Everything is working as intended'
                elif contents[0] == '1000':
                    result = 'Under-voltage was detected, consider getting a uninterruptible power supply for your Raspberry Pi.'
                elif contents[0] == '2000':
                    result = 'Your Raspberry Pi is limited due to a bad powersupply, replace the power supply cable or power supply itself.'
                elif contents[0] == '3000':
                    result = 'Your Raspberry Pi is limited due to a bad powersupply, replace the power supply cable or power supply itself.'
                elif contents[0] == '4000':
                    result = 'The Raspberry Pi is throttled due to a bad power supply this can lead to corruption and instability, please replace your changer and cables.'
                elif contents[0] == '5000':
                    result = 'The Raspberry Pi is throttled due to a bad power supply this can lead to corruption and instability, please replace your changer and cables.'
                elif contents[0] == '8000':
                    result = 'Your Raspberry Pi is overheating, consider getting a fan or heat sinks.'
                else:
                    result = 'There is a problem with your power supply or system.'
                return result

def publish_to_mqtt (cpu_load = 0, cpu_temp = 0, used_space = 0, voltage = 0, sys_clock_speed = 0, swap = 0, memory = 0, uptime = 0, power_supply = 0):
                # connect to mqtt server
                client = paho.Client()
                client.username_pw_set(config.mqtt_user, config.mqtt_password)
                client.connect(config.mqtt_host, config.mqtt_port)

                # publish monitored values to MQTT
                if config.cpu_load:
                        client.publish(config.mqtt_topic_prefix+"/load_1m", cpu_load, qos=1)
                        time.sleep(config.sleep_time)
                if config.cpu_temp:
                        client.publish(config.mqtt_topic_prefix+"/temperature", cpu_temp, qos=1)
                        time.sleep(config.sleep_time)
                if config.used_space:
                        client.publish(config.mqtt_topic_prefix+"/disk_use_percent", used_space, qos=1)
                        time.sleep(config.sleep_time)
                if config.voltage:
                        client.publish(config.mqtt_topic_prefix+"/voltage", voltage, qos=1)
                        time.sleep(config.sleep_time)
                if config.swap:
                        client.publish(config.mqtt_topic_prefix+"/swap", swap, qos=1)
                        time.sleep(config.sleep_time)
                if config.memory:
                        client.publish(config.mqtt_topic_prefix+"/memory_use_percent", memory, qos=1)
                        time.sleep(config.sleep_time)
                if config.sys_clock_speed:
                        client.publish(config.mqtt_topic_prefix+"/sys_clock_speed", sys_clock_speed, qos=1)
                        time.sleep(config.sleep_time)
                if config.uptime:
                        client.publish(config.mqtt_topic_prefix+"/last_boot", uptime, qos=1)
                        time.sleep(config.sleep_time)
                if config.power_supply:
                        client.publish(config.mqtt_topic_prefix+"/rpi_power_status", power_supply, qos=1)
                        time.sleep(config.sleep_time)
                # disconect from mqtt server
                client.disconnect()

def bulk_publish_to_mqtt (cpu_load = 0, cpu_temp = 0, used_space = 0, voltage = 0, sys_clock_speed = 0, swap = 0, memory = 0, uptime = 0, power_supply = 0):
                # compose the CSV message containing the measured values

                values = cpu_load, float(cpu_temp), used_space, float(voltage), int(sys_clock_speed), swap, memory, uptime, power_supply
                values = str(values)[1:-1]

                # connect to mqtt server
                client = paho.Client()
                client.username_pw_set(config.mqtt_user, config.mqtt_password)
                client.connect(config.mqtt_host, int(config.mqtt_port))

                # publish monitored values to MQTT
                client.publish(config.mqtt_topic_prefix+"/"+hostname, values, qos=1)

                # disconect from mqtt server
                client.disconnect()

if __name__ == '__main__':
                # set all monitored values to False in case they are turned off in the config
                cpu_load = cpu_temp = used_space = voltage = sys_clock_speed = swap = memory = uptime = power_supply = False

                # delay the execution of the script
                time.sleep(config.random_delay)

                # collect the monitored values
                if config.cpu_load:
                        cpu_load = check_cpu_load()
                if config.cpu_temp:
                        cpu_temp = check_cpu_temp()
                if config.used_space:
                        used_space = check_used_space('/')
                if config.voltage:
                        voltage = check_voltage()
                if config.sys_clock_speed:
                        sys_clock_speed = check_sys_clock_speed()
                if config.swap:
                        swap = check_swap()
                if config.memory:
                        memory = check_memory()
                if config.uptime:
                        uptime = check_uptime()
                if config.power_supply:
                        power_supply = check_power_supply()
                # Publish messages to MQTT
                if config.group_messages:
                        bulk_publish_to_mqtt(cpu_load, cpu_temp, used_space, voltage, sys_clock_speed, swap, memory, uptime, power_supply)
                else:
                        publish_to_mqtt(cpu_load, cpu_temp, used_space, voltage, sys_clock_speed, swap, memory, uptime, power_supply)