# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import pyodbc
import datetime
import os.path
from threading import Thread

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def dateSQL():
        terazStr = "'" + str(datetime.datetime.now()) + "'"
        data = "CONVERT(datetime2, " + terazStr + ")"
        return data

def sqlInsertStr(stan, dlugosc, czyStartowe, czyOffline):
        ins = 'INSERT INTO Szafa VALUES('
        ins += dateSQL() + "," + str(stan) + "," + str(dlugosc) +","+str(czyStartowe)+","+str(czyOffline)+ ")"
        # print ins
        return ins

def GetConnectionString():

    f = open("/home/Programowanie/Python/SzafaOswietlenie/adres.txt","r")
    ip = f.readline()
    f.close()

    #print ip

    details = {
        'server':  ip,
        'database': 'Dom',
        'username': 'sa',
        'password': 'Zxcvbn1234455!',
    }
    return 'DRIVER={{FreeTDS}};SERVER={server}; DATABASE={database};UID={username};PWD={password};'.format(**details)


class Zapis:
    path="/home/Programowanie/Python/SzafaOswietlenie/temp.txt"

    conn=None
    polaczenie=None

    data_sprawdzenie_polaczenia = datetime.datetime.now()


    minutes_check = 1



    connecting_led=[35]

    def connecting_led_on(self):
        for x_on in self.connecting_led:
            GPIO.output(x_on, GPIO.HIGH)

    def connecting_led_off(self):
        for x_off in self.connecting_led:
            GPIO.output(x_off, GPIO.LOW)

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        for x in self.connecting_led:
            GPIO.setup(x, GPIO.OUT)
        self.connecting_led_off()

        # try:
        #     #raise pyodbc.OperationalError
        #     self.OnConnect()
        # except pyodbc.OperationalError:
        #     self.OnDisconnect()

    def _start(self):
        try:
            #raise pyodbc.OperationalError
            self.OnConnect()
        except pyodbc.OperationalError:
            self.OnDisconnect()



    def OnConnect(self):
        self.conn = pyodbc.connect(GetConnectionString())
        self.polaczenie = True
        self.data_sprawdzenie_polaczenia = None
        print bcolors.WARNING, "POŁĄCZONO Z BAZĄ\n\n", bcolors.ENDC
        if  os.path.isfile(self.path):
            print "\t\tZNALEZIONO PLIK\n\n"
            f = open(self.path,"r")
            lines = f.readlines()
            for line in lines:
                self.conn.cursor().execute(line)
            self.conn.commit()
            os.remove(self.path)

    def OnDisconnect(self):
        self.data_sprawdzenie_polaczenia = datetime.datetime.now() + datetime.timedelta(minutes=self.minutes_check)
        self.polaczenie = False
        print bcolors.WARNING, "\tNIE POŁĄCZONO Z BAZĄ (zapisywanie do pliku)\n\t(ponowna próba za "+str(self.minutes_check)+" min)", bcolors.ENDC

    _thread_running=False

    #wzywana co każdy pomiar w t.py
    def Callback(self):
        if self.polaczenie!=True:
            if datetime.datetime.now() > self.data_sprawdzenie_polaczenia and not self._thread_running:
                self._thread_running = True
                _t = Thread(target=self._callback_thread)
                _t.daemon = True
                _t.start()
                # try:
                #     self.connecting_led_on()
                #     self.OnConnect()
                # except pyodbc.OperationalError:
                #     self.OnDisconnect()
                # finally:
                #     self.connecting_led_off()

    def _callback_thread(self):
        try:
            self.connecting_led_on()
            self.OnConnect()
        except pyodbc.OperationalError:
            self.OnDisconnect()
        finally:
            self.connecting_led_off()
            self._thread_running = False


    def zapisz(self, stan, dlugosc, czyStartowe):
        print "test"
        if self.polaczenie:
            try:
                insert = sqlInsertStr(stan, dlugosc, czyStartowe,0)
                print "Dodano do bazy: ",insert
                self.conn.cursor().execute(insert)
                self.conn.commit()
            except pyodbc.Error:
                self.OnDisconnect()
                self.doPliku(stan, dlugosc, czyStartowe)
        else:
            self.doPliku(stan,dlugosc,czyStartowe)
        print "test2"



    def doPliku(self,stan,dlugosc,czyStartowe):
        insert = sqlInsertStr(stan, dlugosc, czyStartowe, 1)
        print "Dodano do pliku: ", insert
        f = open(self.path, "a")
        f.write(insert + "\n")
        f.close()
