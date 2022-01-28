# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

TRIG = 11
ECHO = 12

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)

# W CENTRYMETRACH # dystans od sensora
def DIS():
    maxTime = 0.04

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    timeOut = pulse_start + maxTime

    while GPIO.input(ECHO) == 0 and pulse_start < timeOut:
        pulse_start = time.time()


    pulse_end = time.time()
    timeOut = pulse_end + maxTime

    while GPIO.input(ECHO) == 1 and pulse_end < timeOut:
        pulse_end = time.time()

    pulse_dur = pulse_end - pulse_start

    Dystans = pulse_dur * 17150
    Dystans = round(Dystans, 2)

    return Dystans
