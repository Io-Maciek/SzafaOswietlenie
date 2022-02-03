# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import datetime
import dis
import zapis


##########################

def led_on():
    for x_on in led:
        GPIO.output(x_on, GPIO.HIGH)


def led_off():
    for x_off in led:
        GPIO.output(x_off, GPIO.LOW)


if __name__ == '__main__':
    print "URUCHOMIONO...\nTRWA ŁĄCZENIE Z BAZĄ DANYCH"

    ### BAZA DANYCH ###

    sql = zapis.Zapis()

    ### GPIO INICJACJA LEDY ###

    led = [36, 37, 38, 40]
    for x in led:
        GPIO.setup(x, GPIO.OUT)

    on = None
    try:
        d = dis.DIS()
        if d > 9.5:
            print "\tWŁĄCZAM\t", datetime.datetime.now()
            led_on()
            sql.zapisz(1, d, 1)
            on = True
        else:
            print "\tOFF\t", datetime.datetime.now()
            sql.zapisz(0, d, 1)
            led_off()
            on = False

        ### PROGRAM ###
        while True:
            d = dis.DIS()
            print d, "\tcm"

            sql.Callback()

            if d > 11.1:
                if not on:
                    print "\tWŁĄCZAM\t", datetime.datetime.now()

                    led_on()
                    sql.zapisz(1, d, 0)
                    on = True
            else:
                if on:
                    print "\tOFF\t", datetime.datetime.now()

                    sql.zapisz(0, d, 0)
                    led_off()
                    on = False

            time.sleep(2)
        ############################# KONIEC
    except KeyboardInterrupt:
        sql.connecting_led_off()
        led_off()
        GPIO.cleanup()
        print "Wyłączono"