import RPi.GPIO as GPIO

class LightingController():
    def __init__(self, light_pin):
        self._is_running = False
        self.pin = light_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def __del__(self):
        GPIO.cleanup()
       
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