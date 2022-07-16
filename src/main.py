from CameraRecorder import PiCameraRecorder as PiCam
from MotionDetector import PIRMotionDetector as PIRSensor
from LightingController import GpioLightingController
from Utilities import Loop
import RPi.GPIO as GPIO
from datetime import datetime as dt
import signal
import sys
import os
from time import sleep
from Utilities import secrets
from FileUtilities import GoogleDriveImageUploaderThreaded as GDriveImageUploader, LatestFileSelector
import pycurl
from ObjectDetector import FaceImageExtractorProcess as FaceExtractor


# Pin control
PIRSENSOR1_PIN = 18
CAM1LIGHT_PIN = 21

# General settings
DATETIME_FORMAT = "%y%m%d%H%M%S"
RECORDING_TIME_SECONDS = 10
GDRIVE_DEV_VERIF_FILE = "device_verif.json"
GDRIVE_BEAR_AND_TOKENS_FILE = "bearer_and_perm_tokens.json"

class App:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print('Received:', signum)
        self.shutdown = True

    def start(self):
        print("Start app")

    def run(self):
        sleep(0.1)

    def stop(self):
        print("Stop app")
        GPIO.cleanup()

if __name__ == '__main__':

    curl = pycurl.Curl()
    jpg_selector = LatestFileSelector.LatestFileSelector("../camera", "jpg")
    mp4_selector = LatestFileSelector.LatestFileSelector("../camera", "mp4")
    #img_uploader_first_config = GDriveImgUploader.GoogleDriveImageUploader(curl_like_object = curl, image_selector=None, device_verif_filename="device_verif.json", bearer_and_perm_tokens_filename="bearer_and_perm_tokens.json", prio=1, interface="eth0", verbose=True)
    #img_uploader_first_config.first_run(GDRIVE_DEV_VERIF_FILE, GDRIVE_BEAR_AND_TOKENS_FILE)
    #del img_uploader_first_config

    app = App()
    app.start()
    cam1_light_control = GpioLightingController.GpioLightingController(CAM1LIGHT_PIN)
    with FaceExtractor.FaceImageExtractorProcess(file_selector=mp4_selector, move_to_path="../camera/analyzed/") as face_extractor_process, \
        GDriveImageUploader.GoogleDriveImageUploaderThreaded(curl_like_object = curl, file_selector=jpg_selector, device_verif_filename=GDRIVE_DEV_VERIF_FILE, bearer_and_perm_tokens_filename=GDRIVE_BEAR_AND_TOKENS_FILE, prio=1, interface="eth0", verbose=True, move_to_path="../camera/uploaded/") as file_uploader_thread:
        with PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, refresh_rate_seconds=1) as pir1_thread:
            with PiCam.PiCameraRecorder(files_path="../camera/", lgt_ctrl=cam1_light_control, picture_prefix=None, video_prefix="video0_", subject=pir1_thread, prio = 0, picture_timestamp=True, video_timestamp=True, rotation=180, framerate=10, resolution=(640, 480), timeout=RECORDING_TIME_SECONDS) as cam1:
                while not app.shutdown:
                    app.run()
            pir1_thread.join(RECORDING_TIME_SECONDS)
        file_uploader_thread.join(10)
    
    app.stop()
    sys.exit(0)

