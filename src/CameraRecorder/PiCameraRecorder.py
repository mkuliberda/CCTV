import time
import datetime
from  picamera import PiCamera
from Observer import observer_abc as AbsObserver
from threading import Thread
from LightingController import *


class PiCameraRecorder(AbsObserver.AbstractObserver):
    def __init__(self, AbstractLightControl, video_path, subject, timestamp=True, timeout=10, resolution=[1280, 760], framerate=20, framerate_range=None, rotation=0):
        self._resolution = resolution
        self._framerate = framerate
        self._framerate_range = framerate_range
        self._rotation = rotation
        self._video_path = video_path
        self._timestamp = timestamp
        self._timeout = timeout
        self._is_recording = False
        self._lgt_ctrl = AbstractLightControl
        self._subject = subject
        self._subject.attach(self)
        
    def update(self, value):
        if self._is_recording == False and value == True:
            recording_thread = Thread(target=self.record)
            recording_thread.start()
            self._is_recording = True

    def __exit__(self, exc_type, exc_value, traceback):
        self._subject.detach(self)
        
    def record(self):
        with PiCamera() as camera:
            now = datetime.datetime.now()
            camera.rotation = self._rotation
            camera.framerate = self._framerate/1
            camera.resolution = self._resolution
            print("recording started...")
            self._lgt_ctrl.turn_on()
            if self._timestamp == True:
                camera.start_recording(self._video_path + '_' + str(now.year) + str(now.month) + str(now.day)+ str(now.hour) + str(now.minute) + str(now.second) + '.h264')
            else:
                camera.start_recording(self._video_path + '.h264')
            time.sleep(self._timeout)
            print("recording stopped")
            camera.stop_recording()
            self._lgt_ctrl.turn_off()
            self._is_recording = False
