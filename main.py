# -*- coding: utf-8 -*-

import os.path

import RPi.GPIO as GPIO
import time
import datetime
from distance import DistanceSensor
import zapis
from serv import Server
from touch import TouchSensor
from config import Config
import sinricpro
from info_diode import InfoLED
from email_service import SMTPService


##########################

def led_on():
    for x_on in led:
        GPIO.output(x_on, GPIO.HIGH)


def led_off():
    for x_off in led:
        GPIO.output(x_off, GPIO.LOW)


def to_on(d):
    global is_overwrite_mode
    if not is_overwrite_mode:
        print("\tWŁĄCZAM\t" + str(datetime.datetime.now()))
        led_on()
    sql.zapisz(1, d, is_overwrite_mode)
    email_smtp.send_new_status(True)


def to_off(d):
    global is_overwrite_mode
    if not is_overwrite_mode:
        print("\tOFF\t" + str(datetime.datetime.now()))
        led_off()
    sql.zapisz(0, d, is_overwrite_mode)
    email_smtp.send_new_status(False)


def alarm_goes_off():
    pass


def set_override(from_sinric_thread=False):
    global is_overwrite_mode, dis, server, config, sinricpro_client, sql
    InfoLED.toggle()
    dis.is_on = False
    led_off()
    is_overwrite_mode = not is_overwrite_mode
    config.override = is_overwrite_mode
    server.update((server.info[0], is_overwrite_mode))
    # sql.Set_Override(is_overwrite_mode)
    config.write()

    if not from_sinric_thread:
        if not config.override:
            sinricpro_client.on()
        else:
            sinricpro_client.off()


def touch(x):
    set_override()


_file = os.path.abspath(__file__)
_parent = os.path.dirname(_file)

##########################

_DELAY = .5

config = Config.read()
print(config)

dis = DistanceSensor(11, 12, distance_trigger=9.6, alarm_minut=config.alarm)
is_overwrite_mode = config.override
InfoLED.init()
touch_sensor = TouchSensor(touch)

sinricpro_client = sinricpro.SinricproConnection(set_override)
sinricpro_client.start()
if not config.override:
    sinricpro_client.on()
else:
    sinricpro_client.off()

if __name__ == '__main__':

    print("URUCHOMIONO...\nTRWA ŁĄCZENIE Z BAZĄ DANYCH:\t", end='')

    ### BAZA DANYCH ###
    sql = None
    if os.path.exists(os.path.join(_parent, 'adres.txt')):
        print('With SQL')
        sql = zapis.Zapis(_parent, is_overwrite_mode)
    else:
        print('No SQL')

    print("ŁĄCZĘ Z SERVEREM SMTP:", end='')
    email_smtp = SMTPService()
    print(f"\t{email_smtp.is_working()}\n")

    ### GPIO INICJACJA LEDY ###

    led = [38, 40]
    for x in led:
        GPIO.setup(x, GPIO.OUT)

    on = None
    try:
        server = Server(debug=True, distance_sensor=dis, override=set_override, parent_path=_parent)
        server.start()
        ### PROGRAM ###
        while True:
            if not is_overwrite_mode:
                d = dis.check_trigger(to_on, to_off, alarm_goes_off)
                print(str(round(d, 2)) + "\tcm")
                server.update((d, is_overwrite_mode))
                if sql is not None:
                    sql.sql_callback()
            else:
                d = dis.check_trigger(to_on, to_off, alarm_goes_off)
                print(str(round(d, 2)) + "\tcm (OV)")
                server.update((d, is_overwrite_mode))
                if sql is not None:
                    sql.sql_callback()
                # if d < dis.max_distance:
                #   is_overwrite_mode = False
            time.sleep(_DELAY)
    except KeyboardInterrupt:
        if sql is not None:
            sql.connecting_led_off()
        if config is not None:
            config.write()
        led_off()
        GPIO.cleanup()
        email_smtp.close()
        print("Wyłączono")
