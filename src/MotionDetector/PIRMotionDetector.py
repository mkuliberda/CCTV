import threading
import RPi.GPIO as GPIO
from Observer import subject_abc as AbsSub
import time


class PIRMotionDetector( AbsSub.AbstractSubject, threading.Thread):
    def __init__(self, detector_pin, refresh_rate_seconds=10):
        self._is_running = True
        self._pin = detector_pin
        self._current_state = False
        self._refresh_rate_seconds = refresh_rate_seconds
        self._dummy_cnt = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)
        threading.Thread.__init__(self)

    def __del__(self):
        GPIO.cleanup()

    def terminate(self):
        self._is_running = False
        
    def run(self):
        while self._is_running:
            self.notify(self.read_pin())
            time.sleep(self._refresh_rate_seconds)

    def get_state(self):
        return self._is_running

    def read_pin(self):
        self._dummy_cnt += 1#
        return  self._dummy_cnt % 2 == 1#not GPIO.input(self._pin)