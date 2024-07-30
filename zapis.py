# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import mysql.connector
import datetime
import os.path
from threading import Thread
from info_diode import InfoLED


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


class Zapis:
    conn = None
    polaczenie = None

    data_sprawdzenie_polaczenia = datetime.datetime.now()

    minutes_check = 1

    def connecting_led_on(self):
        InfoLED.toggle()

    def connecting_led_off(self):
        InfoLED.toggle()

    def __init__(self, parent_path, override):
        GPIO.setmode(GPIO.BOARD)
        InfoLED.init()
        self._parent_path = parent_path
        self.path = os.path.join(parent_path, 'temp.txt')

        #self.connecting_led_off()
        self.set_override = override

        self.sqldb = None
        self._thread_running = False

        f = open(os.path.join(self._parent_path, 'adres.txt'), "r")

        self._ip = f.readline().strip()
        self._database = f.readline().strip()
        self.table = f.readline().strip()
        self._login = f.readline().strip()
        self._password = f.readline().strip()

        f.close()
        self._czy_startowe=True
        self._on_connect()

    def _get_czy_startowe(self):
        temp = self._czy_startowe
        self._czy_startowe = False
        return temp

    def _start(self):
        try:
            self._on_connect()
        except Exception as e:
            print("start fun ||| " + str(e))
            self._on_disconnect()

    def _on_connect(self):
        self.sqldb = mysql.connector.connect(
            host=self._ip,
            user=self._login,
            password=self._password,
            database=self._database,
            port="3306"
        )

        self.polaczenie = True
        self.data_sprawdzenie_polaczenia = datetime.datetime.now()
        print(bcolors.WARNING + "POŁĄCZONO Z BAZĄ\n\n" + bcolors.ENDC)
        
        mycursor = self.sqldb.cursor()

        mycursor.execute(
                "INSERT INTO " + self.table + " (Data, Stan, Dlugosc, CzyStartowe, CzyOffline, CzyNadpis) VALUES (%s, %s, %s, %s, false, %s);",
                (datetime.datetime.now(), True, 37, True, True)
        )

        self.sqldb.commit()


        if os.path.isfile(self.path):
            print("\t\tZNALEZIONO PLIK\n\n")
            f = open(self.path, "r")
            lines = f.readlines()
            mycursor = self.sqldb.cursor()
            for line in lines:

                mycursor.execute(
                    line
                )

            self.sqldb.commit()
            os.remove(self.path)

    def _on_disconnect(self):
        self.data_sprawdzenie_polaczenia = datetime.datetime.now() + datetime.timedelta(minutes=self.minutes_check)
        self.polaczenie = False
        print(bcolors.WARNING + "\tNIE POŁĄCZONO Z BAZĄ (zapisywanie do pliku)\n\t(ponowna próba za " + str(
            self.minutes_check) + " min)" + bcolors.ENDC)

    def sql_callback(self):
        """
        Wzywana co każdy pomiar w main.py
        Sprawdza połączenie z bazą danych, ewentualnie próbuje się z nią połączyć
            na innym procesie
        """
        if not self.polaczenie:
            if datetime.datetime.now() > self.data_sprawdzenie_polaczenia and not self._thread_running:
                self._thread_running = True
                _t = Thread(target=self._callback_thread)
                _t.daemon = True
                _t.start()

    def _callback_thread(self):
        try:
            self.connecting_led_on()
            self._on_connect()
        except Exception as e:
            print("Callback exceptions : " + str(e))
            self._on_disconnect()
        finally:
            self.connecting_led_off()
            self._thread_running = False

    def zapisz(self, stan, dlugosc, czyNadpis):
        try:
            # insert = sqlInsertStr(stan, dlugosc, czyStartowe, 0)
            mycursor = self.sqldb.cursor()

            mycursor.execute(
                "INSERT INTO " + self.table + " (Data, Stan, Dlugosc, CzyStartowe, CzyOffline, CzyNadpis) VALUES (%s, %s, %s, %s, false, %s);",
                (datetime.datetime.now(), stan, dlugosc, self._get_czy_startowe(), czyNadpis)
            )

            self.sqldb.commit()
        except Exception as e:
            print("zapis exception : " + str(e))
            self._on_disconnect()
            query = f"INSERT INTO {self.table} (Data, Stan, Dlugosc, CzyStartowe, CzyOffline, CzyNadpis) VALUES " \
                    f"('{datetime.datetime.now()}', {stan}, {dlugosc}, {self._get_czy_startowe()}, true, {czyNadpis});"
            self.do_pliku(query)

    def do_pliku(self, query):
        f = open(self.path, "a")
        f.write(query + "\n")
        f.close()
