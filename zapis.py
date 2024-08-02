# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import mysql.connector
import datetime
import os.path
from threading import Thread
from info_diode import InfoLED
from loguru import logger


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

        # self.connecting_led_off()
        self.set_override = override

        self.sqldb = None
        self._thread_running = False
        self._czy_startowe = True

        try:
            f = open(os.path.join(self._parent_path, 'adres.txt'), "r")
            self._ip = f.readline().strip()
            self._database = f.readline().strip()
            self.table = f.readline().strip()
            self._login = f.readline().strip()
            self._password = f.readline().strip()

            self.__plik_nie_istnieje_nie_lacz_sie = False
            f.close()
            self._on_connect()
        except FileNotFoundError:
            self.polaczenie = False
            self.__plik_nie_istnieje_nie_lacz_sie = True
            logger.info("Nie ustawiono połączenia z bazą danych SQL.")
            # self._on_disconnect()
        except Exception:
            logger.exception("Błąd podczas odczytywania pliku SQL.")

    def _get_czy_startowe(self):
        temp = self._czy_startowe
        self._czy_startowe = False
        return temp

    def _start(self):
        if not self.__plik_nie_istnieje_nie_lacz_sie:
            try:
                self._on_connect()
            except Exception as e:
                self._on_disconnect()

    def _on_connect(self):
        if not self.__plik_nie_istnieje_nie_lacz_sie:
            self.sqldb = mysql.connector.connect(
                host=self._ip,
                user=self._login,
                password=self._password,
                database=self._database,
                port="3306"
            )

            self.polaczenie = True
            self.data_sprawdzenie_polaczenia = datetime.datetime.now()
            logger.success("Połączono z bazą danych SQL.")

            mycursor = self.sqldb.cursor()

            mycursor.execute(
                "INSERT INTO " + self.table + " (Data, Stan, Dlugosc, CzyStartowe, CzyOffline, CzyNadpis) VALUES (%s, %s, %s, %s, false, %s);",
                (datetime.datetime.now(), True, 37, True, True)
            )

            self.sqldb.commit()

            if os.path.isfile(self.path):
                logger.info("Znaleziono plik TEMP.")
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
        if not self.__plik_nie_istnieje_nie_lacz_sie:
            self.data_sprawdzenie_polaczenia = datetime.datetime.now() + datetime.timedelta(minutes=self.minutes_check)
            self.polaczenie = False

            logger.warning("Nie można było ustalić połączenia z bazą danych SQL.")

    def sql_callback(self):
        """
        Wzywana co każdy pomiar w main.py
        Sprawdza połączenie z bazą danych, ewentualnie próbuje się z nią połączyć
            na innym procesie
        """
        if not self.__plik_nie_istnieje_nie_lacz_sie:
            if not self.polaczenie:
                if datetime.datetime.now() > self.data_sprawdzenie_polaczenia and not self._thread_running:
                    self._thread_running = True
                    _t = Thread(target=self._callback_thread)
                    _t.daemon = True
                    _t.start()

    @logger.catch
    def _callback_thread(self):
        try:
            self.connecting_led_on()
            self._on_connect()
        except Exception:
            logger.exception("SQL callback exception?")
            self._on_disconnect()
        finally:
            self.connecting_led_off()
            self._thread_running = False

    def zapisz(self, stan, dlugosc, czyNadpis):
        if not self.__plik_nie_istnieje_nie_lacz_sie:
            if self.polaczenie:
                try:
                    # insert = sqlInsertStr(stan, dlugosc, czyStartowe, 0)
                    mycursor = self.sqldb.cursor()

                    mycursor.execute(
                        "INSERT INTO " + self.table + " (Data, Stan, Dlugosc, CzyStartowe, CzyOffline, CzyNadpis) VALUES (%s, %s, %s, %s, false, %s);",
                        (datetime.datetime.now(), stan, dlugosc, self._get_czy_startowe(), czyNadpis)
                    )

                    self.sqldb.commit()
                    logger.success("Zapisano w bazie danych SQL.")
                except Exception:
                    logger.exception("SQL saving exception?")
                    self._on_disconnect()
                    query = f"INSERT INTO {self.table} (Data, Stan, Dlugosc, CzyStartowe, CzyOffline, CzyNadpis) VALUES " \
                            f"('{datetime.datetime.now()}', {stan}, {dlugosc}, {self._get_czy_startowe()}, true, {czyNadpis});"
                    self.do_pliku(query)
                    logger.warning("Zapisano w pliku tymczasowym TEMP.")

    def do_pliku(self, query):
        f = open(self.path, "a")
        f.write(query + "\n")
        f.close()
