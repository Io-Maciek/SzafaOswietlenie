import RPi.GPIO as GPIO


class TouchSensor:
    def __init__(self, callback=lambda x: None, pin_number=7):
        self.is_active = False

        GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(pin_number, GPIO.RISING, callback=callback, bouncetime=300)


if __name__ == '__main__':
    def p(x):
        print ('test' + str(x))
        
    touch_sensor = TouchSensor(p)
    while True:
        pass