# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import datetime
from dis import Distance
import zapis


##########################

def led_on():
    for x_on in led:
        GPIO.output(x_on, GPIO.HIGH)


def led_off():
    for x_off in led:
        GPIO.output(x_off, GPIO.LOW)


def to_on(d):
    print "\tWŁĄCZAM\t", datetime.datetime.now()
    led_on()
    sql.zapisz(1, d, 0)


def to_off(d):
    print "\tOFF\t", datetime.datetime.now()
    sql.zapisz(0, d, 0)
    led_off()


def alarm_goes_off():
    pass


##########################

_DELAY = .5
dis = Distance(11, 12, 11.1, alarm_minut=0.1)

if __name__ == '__main__':
    print "URUCHOMIONO...\nTRWA ŁĄCZENIE Z BAZĄ DANYCH"

    ### BAZA DANYCH ###

    sql = zapis.Zapis()

    ### GPIO INICJACJA LEDY ###

    led = [38, 40]
    for x in led:
        GPIO.setup(x, GPIO.OUT)

    on = None
    try:
        ### PROGRAM ###
        while True:
            d = dis.check_trigger(to_on, to_off, alarm_goes_off)
            print round(d, 2), "\tcm"
            sql.Callback()
            time.sleep(_DELAY)
    except KeyboardInterrupt:
        sql.connecting_led_off()
        led_off()
        GPIO.cleanup()
        print "Wyłączono"
