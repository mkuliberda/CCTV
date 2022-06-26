from datetime import datetime as dt
from  picamera import PiCamera
from Observer import observer_abc as AbsObserver
from threading import Thread
from LightingController import *
from FileUtilities import FileDeleter
from PriorityManager import SimplePriorityManager as PrioMgr

RECORDING_DATETIME_FMT = "%y%m%d%H%M%S"


class PiCameraRecorder(AbsObserver.AbstractObserver, PrioMgr.SimplePriorityManager):
    def __init__(self, AbstractLightControl, subject, prio, datetime_fmt=RECORDING_DATETIME_FMT, video_scheme="", picture_scheme="", picture_timestamp=False, video_timestamp=True, timeout=10, resolution=None, framerate=20, framerate_range=None, rotation=0):
        PrioMgr.SimplePriorityManager.__init__(self)
        self.set_priority(prio)
        if resolution is None:
            resolution = (1280, 760)
        self._resolution = resolution
        self._framerate = framerate
        self._framerate_range = framerate_range
        self._rotation = rotation
        self._video_scheme = video_scheme
        self._picture_scheme = picture_scheme
        self._video_timestamp = video_timestamp
        self._picture_timestamp = picture_timestamp
        self._timeout = timeout
        self._is_recording = False
        self._lgt_ctrl = AbstractLightControl
        self._subject = subject
        self._datetime_fmt = datetime_fmt
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
            now_str = dt.now().strftime(self._datetime_fmt)
            camera.rotation = self._rotation
            camera.framerate = self._framerate/1
            camera.resolution = self._resolution
            
            with FileDeleter.FileDeleter("h264", path="camera", files_limit=30) as video_cleaner,\
                 FileDeleter.FileDeleter("jpg", path="camera", files_limit=50) as jpg_cleaner:
                video_cleaner.run()
                jpg_cleaner.run()

            self._lgt_ctrl.turn_on()
            if self._picture_timestamp is True:
                camera.capture(self._picture_scheme + '_' + now_str + '.jpg')
            else:
                camera.capture(self._picture_scheme + '.jpg')

            print("recording started...")
            if self._video_timestamp is True:
                camera.start_recording(self._video_scheme + '_' + now_str + '.h264')
            else:
                camera.start_recording(self._video_scheme + '.h264')
            camera.wait_recording(self._timeout)
            camera.stop_recording()
            print("recording stopped")
            self._lgt_ctrl.turn_off()
            self._is_recording = False
