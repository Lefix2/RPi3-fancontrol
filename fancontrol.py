#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
import signal
import sys
import os

from gpiozero import OutputDevice


MAX_TEMP = 63  # (degrees Celsius) Fan kicks on at this temperature.
MIN_TEMP = 55  # (degrees Celsius) Fan shuts off at this temperature.
HYS_TEMP = 3   # (degrees Celsius) Temp hysteresis
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
    fan.ChangeDutyCycle(speed)
    return()

def handleFanSpeed(last_temp, heating_up):
    temp = get_temp()
    delta = temp - last_temp
    print(f"temp: {temp:.2f}°C [ {last_temp:.2f}{delta:+.2f}°C {'^' if heating_up else 'v'}]")

    if not((delta != 0 and (delta > 0) == heating_up) or abs(delta) > HYS_TEMP or ((temp <= MIN_TEMP) and heating_up) or ((temp >= MAX_TEMP) and not heating_up)):
        return last_temp, heating_up


    if temp < MIN_TEMP:
        fan_speed = FAN_OFF

    elif temp > MAX_TEMP:
        fan_speed = FAN_MAX

    else:
        fan_speed = FAN_LOW + ((temp-MIN_TEMP)*(FAN_HIGH-FAN_LOW))/(MAX_TEMP-MIN_TEMP)

    print(f"* Setting fan speed to {fan_speed:.1f}%")
    setFanSpeed(fan_speed)

    return temp, (delta > 0)

if __name__ == '__main__':
    # Validate the on and off thresholds
    if MIN_TEMP >= MAX_TEMP:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT, initial=GPIO.LOW)
    fan = GPIO.PWM(GPIO_PIN, PWM_FREQ)
    fan.start(FAN_OFF)

    last_temp = 0;
    heating_up = True

    while True:
        last_temp, heating_up = handleFanSpeed(last_temp, heating_up)
        time.sleep(SLEEP_INTERVAL)
