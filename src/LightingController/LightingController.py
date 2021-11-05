import RPi.GPIO as GPIO
from Observer import observer_abc as AbsObserver

class LightingController(AbsObserver.AbstractObserver):
    def __init__(self, light_pin):
        self._is_running = False
        self.pin = light_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def __del__(self):
        GPIO.cleanup()

    def __exit__(self, exc_type, exc_value, traceback):
        GPIO.cleanup()
        self._subjects.detach(self)
 
    def update(self, value):
        if value == True:
            self.turnON()
        else:
            self.turnOFF()
        
    def turnON(self):
        print("light on")
        GPIO.output(self.pin, GPIO.HIGH)
        self._is_running = True
        
    def turnOFF(self):
        print("light off")
        GPIO.output(self.pin, GPIO.LOW)
        self._is_running = False
        
    def getState(self):
        return self._is_running