# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import datetime
import dis
import zapis

##########################

def ON():
    for x in led:
        GPIO.output(x, GPIO.HIGH)

def OFF():
    for x in led:
        GPIO.output(x, GPIO.LOW)

if __name__ == '__main__':
    ##########################

    print "URUCHOMIONO...\nTRWA ŁĄCZENIE Z BAZĄ DANYCH"

    ### BAZA DANYCH ###

    sql = zapis.Zapis()

    ###   ###


    ### GPIO INICJACJA LEDY ###

    led=[36,37,38,40]
    for x in led:
        GPIO.setup(x, GPIO.OUT)

    ###   ###

    on = None
    try:
        d = dis.DIS()
        if (d > 9.5):
            print "\tWLACZAM\t", datetime.datetime.now()
            ON()
            sql.zapisz(1, d,1)
            on = True
        else:
            print "\tOFF\t", datetime.datetime.now()
            sql.zapisz(0, d,1)
            OFF()
            on = False

        ### PROGRAM ###
        while True:
            d = dis.DIS()
            print d,"\tcm"

            sql.Callback()

            if(d>11.1):
                if(on==False):
                    print "\tWLACZAM\t",datetime.datetime.now()

                    ON()
                    sql.zapisz(1,d,0)
                    on = True
            else:
                if(on==True):
                    print "\tOFF\t",datetime.datetime.now()

                    sql.zapisz(0,d,0)
                    OFF()
                    on=False


            time.sleep(2)
        ############################# KONIEC
    except KeyboardInterrupt:
        OFF()
        GPIO.cleanup()
        print "Wylaczono"
    # finally:
    #     OFF()
    #     GPIO.cleanup()
    #     print "Wylaczono"