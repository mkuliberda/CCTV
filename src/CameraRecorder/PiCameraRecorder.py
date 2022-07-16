from datetime import datetime as dt
from picamera import PiCamera
from Observer import observer_abc as AbsObserver
from threading import Thread
from LightingController import *
from PriorityManager import SimplePriorityManager as PrioMgr
import logging


RECORDING_DATETIME_FMT = "%y%m%d%H%M%S"


class PiCameraRecorder(AbsObserver.AbstractObserver, PrioMgr.SimplePriorityManager):
    def __init__(self, lgt_ctrl, subject, prio, files_path="", datetime_fmt=RECORDING_DATETIME_FMT, video_prefix=None, video_ext="h264", picture_prefix=None, picture_ext="jpg", picture_timestamp=False, video_timestamp=True, timeout=10, resolution=None, framerate=20, framerate_range=None, rotation=0):
        PrioMgr.SimplePriorityManager.__init__(self)
        self.set_priority(prio)
        if resolution is None:
            resolution = (1280, 760)
        self._resolution = resolution
        self._framerate = framerate
        self._framerate_range = framerate_range
        self._rotation = rotation
        self._video_prefix = video_prefix
        self._video_ext = video_ext
        self._picture_prefix = picture_prefix
        self._picture_ext = picture_ext
        self._video_timestamp = video_timestamp
        self._picture_timestamp = picture_timestamp
        self._timeout = timeout
        self._is_recording = False
        self._lgt_ctrl = lgt_ctrl
        self._subject = subject
        self._datetime_fmt = datetime_fmt
        self._files_path = files_path
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
            #camera.color_effects = [128, 128]

            self._lgt_ctrl.turn_on()

            if self._picture_prefix is not None:
                if self._picture_timestamp is True:
                    image_file_relative = self._files_path + self._picture_prefix + now_str + '.' + self._picture_ext
                else:
                    image_file_relative = self._files_path + self._picture_prefix + '.' + self._picture_ext
                camera.capture(image_file_relative)

            if self._video_prefix is not None:
                logging.info("recording...")
                print("recording...")
                if self._video_timestamp is True:
                    video_file_relative = self._files_path + self._video_prefix + str(self._framerate) + "fps" + now_str
                else:
                    video_file_relative = self._files_path + self._video_prefix + str(self._framerate) + "fps"
                video_file_relative_with_ext = video_file_relative + "." + self._video_ext
                camera.start_recording(video_file_relative_with_ext)
                camera.wait_recording(self._timeout)
                camera.stop_recording()
                print("recording stop")
                logging.info("recording stop")
                self._is_recording = False

            self._lgt_ctrl.turn_off()
