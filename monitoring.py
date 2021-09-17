import os
import datetime
import ffmpeg
import time
import threading
import picamera
import io
import itertools
import RPi.GPIO as GPIO


# Pin control
PIRSENSOR_PIN = 18
LIGHTING_PIN = 19

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

class MovementDetector(threading.Thread):
    def __init__(self, detector_pin):
        print("MovementDetector ctor")
        self._is_running = True
        self._pin = detector_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)
        self._counter = 0
        threading.Thread.__init__(self)

    def __del__(self):
        print ("MovementDetector dtor")
        GPIO.cleanup()

    def terminate(self):
        self._is_running = False
        
    def run(self):
        while self._is_running:
            if self._counter < 5:
                with picamera.PiCamera() as camera:
                    camera.rotation = 180
                    now = datetime.datetime.now()
                    camera.start_recording("/dev/video0".split('/')[-1] + '_' + str(now.year) + str(now.month) + str(now.day)+ str(now.hour) + str(now.minute) + str(now.second) + '.h264')
                    camera.wait_recording(5)
                    camera.stop_recording()
                    print("cycle: " + str(self._counter))
                    self._counter += 1
            else:
                self.terminate()

    def getState(self):
        return self._is_running

def record(video_path):
    now = datetime.datetime.now()
    stream = ffmpeg.input(video_path)
    stream = ffmpeg.vflip(stream)
    stream = ffmpeg.hflip(stream)
    stream = ffmpeg.output(stream, video_path.split('/')[-1] + '_' + str(now.year) + str(now.month) + str(now.day)+ str(now.hour) + str(now.minute) + str(now.second) + '.mp4')
    ffmpeg.run(stream)


def record_PiCamera(video_path, timeout=10):
    now = datetime.datetime.now()
    camera = PiCamera()
    camera.rotation = 180
    
    camera.start_recording(video_path.split('/')[-1] + '_' + str(now.year) + str(now.month) + str(now.day)+ str(now.hour) + str(now.minute) + str(now.second) + '.h264')
    time.sleep(timeout)
    camera.stop_recording()

def record_USBWebCam(video_path):
    pass


print("Hello world")

#record_PiCamera('/dev/video0')
detector = MovementDetector(PIRSENSOR_PIN)
detector.start()

time.sleep(30)

detector.join()
del detector







    