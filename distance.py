# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import datetime


class DistanceSensor:
    def __init__(self, trigger_pin=11, echo_pin=12, distance_trigger=10.0, alarm_minut=0.5):
        GPIO.setmode(GPIO.BOARD)

        self.TRIG = trigger_pin
        self.ECHO = echo_pin
        self.max_distance = distance_trigger
        self.is_on = None
        self.minuty_alarm = alarm_minut

        self._set_alarm = None

        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

        GPIO.output(self.TRIG, False)

    """
    Dystans w centymetrach od sensora
    """

    def measure(self):
        maxTime = .1#0.04

        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        pulse_start = time.time()
        timeOut = pulse_start + maxTime

        while GPIO.input(self.ECHO) == 0 and pulse_start < timeOut:
            pulse_start = time.time()

        pulse_end = time.time()
        timeOut = pulse_end + maxTime

        while GPIO.input(self.ECHO) == 1 and pulse_end < timeOut:
            pulse_end = time.time()

        pulse_dur = pulse_end - pulse_start

        return pulse_dur * 17150

    def check_trigger(self, changed_to_on, changed_to_off, alarm_trigger=lambda: None):
        d = self.measure()
        if d > self.max_distance:
            if not self.is_on:
                changed_to_on(d)
                self._set_alarm = datetime.datetime.now() + datetime.timedelta(minutes=self.minuty_alarm)
                self.is_on = True
            elif datetime.datetime.now() >= self._set_alarm:
                alarm_trigger()
        else:
            if self.is_on:
                changed_to_off(d)
                self.is_on = False
        return d
