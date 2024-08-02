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
from loguru import logger

##########################
GPIO.setwarnings(False)


def led_on():
    for x_on in led:
        GPIO.output(x_on, GPIO.HIGH)


def led_off():
    for x_off in led:
        GPIO.output(x_off, GPIO.LOW)


def to_on(d):
    global is_overwrite_mode
    if not is_overwrite_mode:
        led_on()
    sql.zapisz(1, d, is_overwrite_mode)
    email_smtp.send_new_status(True)


def to_off(d):
    global is_overwrite_mode
    if not is_overwrite_mode:
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


if __name__ == '__main__':
    _DELAY = .5
    _file = os.path.abspath(__file__)
    _parent = os.path.dirname(_file)

    ##########################

    logger.add("logs.log", mode='w', encoding="utf-8")
    logger.info("Inicjalizuje program.")
    config = Config.read()
    logger.debug(f"Config:\t{config}")

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

    ### BAZA DANYCH ###

    sql = None
    if os.path.exists(os.path.join(_parent, 'adres.txt')):
        # logger.success ("Połączono z bazą danych SQL.")
        sql = zapis.Zapis(_parent, is_overwrite_mode)
    else:
        pass
        # logger.warning ("Nie połączono z bazą danych SQL.")

    email_smtp = SMTPService()
    if email_smtp.is_working():
        logger.success("Połączono z serwerem SMTP.")
    else:
        logger.warning("Nie połączono z serwerem SMTP.")

    ### GPIO INICJACJA LEDY ###

    led = [38, 40]
    for x in led:
        GPIO.setup(x, GPIO.OUT)

    on = None
    try:
        server = Server(debug=True, distance_sensor=dis, override=set_override, parent_path=_parent, port=7999)
        server.start()
        ### PROGRAM ###
        logger.info("Uruchomiono program.")

        while True:

            if not is_overwrite_mode:
                d = dis.check_trigger(to_on, to_off, is_overwrite_mode, alarm_goes_off)
                server.update((d, is_overwrite_mode))
            else:
                d = dis.check_trigger(to_on, to_off, is_overwrite_mode, alarm_goes_off)
                server.update((d, is_overwrite_mode))

            if sql is not None:
                sql.sql_callback()

            time.sleep(_DELAY)

    except KeyboardInterrupt:
        if sql is not None:
            sql.connecting_led_off()
        if config is not None:
            config.write()
        led_off()
        GPIO.cleanup()
        email_smtp.close()
        logger.info("Program wyłączony.")
