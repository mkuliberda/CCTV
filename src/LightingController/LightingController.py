import RPi.GPIO as GPIO
from Observer import AbstractObserver

class LightingController():
    def __init__(self, light_pin):
        self._is_running = False
        self.pin = light_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin,GPIO.OUT)

    def __del__(self):
        GPIO.cleanup()
        
    def turnON(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self._is_running = True
        
    def turnOFF(self):
        GPIO.output(self.pin, GPIO.LOW)
        self._is_running = False
        
    def getStatus(self):
        return self._is_running