import RPi.GPIO as GPIO
from LightingController import AbstractLightControl as AbsLgtCtrl


class GpioLightingController(AbsLgtCtrl.AbstractLightControl):
    def __init__(self, light_pin):
        self._is_running = False
        self.pin = light_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=0)

    def __del__(self):
        GPIO.cleanup()
      
    def turn_on(self):
        print("light on")
        GPIO.output(self.pin, GPIO.HIGH)
        self._is_running = True
        
    def turn_off(self):
        print("light off")
        GPIO.output(self.pin, GPIO.LOW)
        self._is_running = False
        
    def get_state(self):
        return self._is_running
