import RPi.GPIO as GPIO
from config import Config


class InfoLED:
    state = False
    connecting_led = 35
    initialized = False

    @staticmethod
    def init():
        if not InfoLED.initialized:
            GPIO.setup(InfoLED.connecting_led, GPIO.OUT)
            config = Config.read()

            if config.override:
                GPIO.output(InfoLED.connecting_led, GPIO.HIGH)
                InfoLED.state = True
            else:
                GPIO.output(InfoLED.connecting_led, GPIO.LOW)
            InfoLED.initialized = True


    @staticmethod
    def toggle():
        if not InfoLED.initialized:
            raise Exception("Class not initialized! Use method InfoLED.init()")

        InfoLED.state = not InfoLED.state
        if InfoLED.state: #turn on
            GPIO.output(InfoLED.connecting_led, GPIO.HIGH)
        else: #turn off
            GPIO.output(InfoLED.connecting_led, GPIO.LOW)
