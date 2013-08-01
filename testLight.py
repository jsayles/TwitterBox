#!/usr/bin/python

import RPi.GPIO as GPIO
import time

LIGHT_PIN=4
LIGHT_DELAY=10

GPIO.setmode(GPIO.BCM) 
GPIO.setup(LIGHT_PIN, GPIO.OUT) 
GPIO.output(LIGHT_PIN, GPIO.LOW)

GPIO.output(LIGHT_PIN, GPIO.HIGH)
time.sleep(LIGHT_DELAY)
GPIO.output(LIGHT_PIN, GPIO.LOW)
