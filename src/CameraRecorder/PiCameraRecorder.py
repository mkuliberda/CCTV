import time
import datetime
from  picamera import PiCamera
from Observer import observer_abc as AbsObserver
from threading import Thread
from LightingController import *
from FileUtilities import FileSanitizer


class PiCameraRecorder(AbsObserver.AbstractObserver):
    def __init__(self, AbstractLightControl, subject,  video_path="", picture_path="", picture_timestamp=False, video_timestamp=True, timeout=10, resolution=None, framerate=20, framerate_range=None, rotation=0):
        if resolution is None:
            resolution = [1280, 760]
        self._resolution = resolution
        self._framerate = framerate
        self._framerate_range = framerate_range
        self._rotation = rotation
        self._video_path = video_path
        self._picture_path = picture_path
        self._video_timestamp = video_timestamp
        self._picture_timestamp = picture_timestamp
        self._timeout = timeout
        self._is_recording = False
        self._lgt_ctrl = AbstractLightControl
        self._subject = subject
        self._subject.attach(self)
        
    def update(self, value):
        if self._is_recording is False and value is True:
            recording_thread = Thread(target=self.record)
            recording_thread.start()
            self._is_recording = True

    def __exit__(self, exc_type, exc_value, traceback):
        self._subject.detach(self)
        
    def record(self):
        with PiCamera() as camera:
            now = datetime.datetime.now()
            timestamp_formatted = str(now.year) + str(now.month) + str(now.day) + "{:02d}".format(now.hour) + "{:02d}".format(now.minute) + "{:02d}".format(now.second)
            camera.rotation = self._rotation
            camera.framerate = self._framerate/1
            camera.resolution = self._resolution
            
            with FileSanitizer.FileSanitizer() as file_sanitizer:
                file_sanitizer.run()

            self._lgt_ctrl.turn_on()
            if self._picture_timestamp is True:
                camera.capture(self._picture_path + '_' + timestamp_formatted + '.jpg')
            else:
                camera.capture(self._picture_path + '.jpg')

            print("recording started...")
            if self._video_timestamp is True:
                camera.start_recording(self._video_path + '_' + timestamp_formatted + '.h264')
            else:
                camera.start_recording(self._video_path + '.h264')
            camera.wait_recording(self._timeout)
            camera.stop_recording()
            print("recording stopped")
            self._lgt_ctrl.turn_off()
            self._is_recording = False
