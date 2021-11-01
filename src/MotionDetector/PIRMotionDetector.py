import threading
import RPi.GPIO as GPIO
from Observer import subject_abc as AbsSub
import time


#TODO: observer design pattern as Subject to implement here
class PIRMotionDetector( AbsSub.AbstractSubject, threading.Thread):
    def __init__(self, detector_pin, refresh_rate_seconds=10):
        print("PIRMotionDetector ctor")
        self._is_running = True
        self._pin = detector_pin
        self._previous_state = False
        self._current_state = False
        self._refresh_rate_seconds = refresh_rate_seconds
        self._dummy_cnt = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)
        threading.Thread.__init__(self)

    def __del__(self):
        print ("PIRMotionDetector dtor")
        GPIO.cleanup()

    def terminate(self):
        self._is_running = False
        
    def run(self):
        while self._is_running:
            self._current_state = self.read_pin()
            print(self._is_running, self._current_state)
            if self._current_state != self._previous_state:
                self.notify()
                print("notify")
                self._previous_state = self._current_state
            time.sleep(self._refresh_rate_seconds)

    def get_state(self):
        return self._is_running

    def read_pin(self):
        self._dummy_cnt += 1#
        return  self._dummy_cnt % 2 == 1#not GPIO.input(self._pin)