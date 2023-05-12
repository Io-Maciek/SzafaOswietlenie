# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import datetime
from dis import DistanceSensor
import zapis
from serv import Server
from touch import TouchSensor


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


def set_override():
    global is_overwrite_mode, dis, server
    dis.is_on = False
    led_off()
    is_overwrite_mode = not is_overwrite_mode
    server.update((server.info[0], is_overwrite_mode))

    
def touch(x):
    set_override()
        
    


##########################

_DELAY = .5
dis = DistanceSensor(11, 12, 11.1, alarm_minut=0.1)

is_overwrite_mode = False
touch_sensor = TouchSensor(touch)

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
        server = Server(debug=True, distance_sensor=dis, override=set_override)
        server.start()
        ### PROGRAM ###
        while True:
            if not is_overwrite_mode:
                d = dis.check_trigger(to_on, to_off, alarm_goes_off)
                print round(d, 2), "\tcm"
                server.update((d, is_overwrite_mode))
                sql.Callback()
            else:
                d = dis.measure()
                print round(d, 2), "\tcm (OV)"
                server.update((d, is_overwrite_mode))
                #if d < dis.max_distance:
                 #   is_overwrite_mode = False
            time.sleep(_DELAY)
    except KeyboardInterrupt:
        sql.connecting_led_off()
        led_off()
        GPIO.cleanup()
        print "Wyłączono"
