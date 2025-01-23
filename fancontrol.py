#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
import signal
import sys
import os

from gpiozero import OutputDevice


MAX_TEMP = 70  # (degrees Celsius) Fan kicks on at this temperature.
MIN_TEMP = 55  # (degress Celsius) Fan shuts off at this temperature.
FAN_LOW = 40
FAN_HIGH = 100
FAN_OFF = 0
FAN_ON = 100
SLEEP_INTERVAL = 1  # (seconds) How often we check the core temperature.
GPIO_PIN = 12  # Which GPIO pin you're using to control the fan.
PWM_FREQ = 25


def get_temp():
    """Get the core temperature.

    Read file from /sys to get CPU temp in temp in C *1000

    Returns:
        int: The core temperature in thousanths of degrees Celsius.
    """
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp_str = f.read()

    try:
        return int(temp_str) / 1000
    except (IndexError, ValueError,) as e:
        raise RuntimeError('Could not parse temperature output.') from e

def setFanSpeed(speed):
    fan.start(speed)
    return()

def handleFanSpeed():
    temp = get_temp()
    print("temp is", temp)

    if temp < MIN_TEMP:
        fan_speed = FAN_OFF

    elif temp > MAX_TEMP:
        fan_speed = FAN_MAX

    else:
        fan_speed = FAN_LOW + ((temp-MIN_TEMP)*(FAN_HIGH-FAN_LOW))/(MAX_TEMP-MIN_TEMP)

    print("Setting fan speed to ", fan_speed)
    setFanSpeed(fan_speed)

    return()

if __name__ == '__main__':
    # Validate the on and off thresholds
    if MIN_TEMP >= MAX_TEMP:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT, initial=GPIO.LOW)
    fan = GPIO.PWM(GPIO_PIN, PWM_FREQ)
    setFanSpeed(FAN_OFF)

    while True:
        handleFanSpeed()
        time.sleep(SLEEP_INTERVAL)
