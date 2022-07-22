import threading
import RPi.GPIO as GPIO
from Observer import subject_abc as AbsSub
import time
import logging


class PIRMotionDetector( AbsSub.AbstractSubject, threading.Thread):
    def __init__(self, detector_pin, refresh_rate_seconds=10):
        self._is_running = True
        self._pin = detector_pin
        self._current_state = False
        self._refresh_rate_seconds = refresh_rate_seconds
        self._true_state_cnt = 0
        self._true_state_cnt_action = 3
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        threading.Thread.__init__(self)
        self.start()

    def terminate(self):
        self._is_running = False
        
    def run(self):
        while self._is_running:
            if self.read_pin() is True:
                self._true_state_cnt += 1
            else:
                self._true_state_cnt = 0
            print("PIR detection: {}".format("Yes" if self._true_state_cnt > self._true_state_cnt_action else "No "), end='\r')
            self.notify(self._true_state_cnt > self._true_state_cnt_action)
            time.sleep(self._refresh_rate_seconds)

    def get_state(self):
        return self._is_running

    def read_pin(self):
        return GPIO.input(self._pin) == 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()
        self._observers.clear()
