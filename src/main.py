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
from FileUtilities import GoogleDriveImageUploader as GDriveImgUploader, LatestImageSelector
import pycurl


# Pin control
PIRSENSOR1_PIN = 18
CAM1LIGHT_PIN = 23

# General settings
DATETIME_FORMAT = "%y%m%d%H%M%S"
RECORDING_TIME_SECONDS = 30
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
    img_selector = LatestImageSelector.LatestImageSelector("../camera", "jpg")
    #img_uploader_first_config = GDriveImgUploader.GoogleDriveImageUploader(curl_like_object = curl, image_selector=None, device_verif_filename="device_verif.json", bearer_and_perm_tokens_filename="bearer_and_perm_tokens.json", prio=1, interface="eth0", verbose=True)
    #img_uploader_first_config.first_run(GDRIVE_DEV_VERIF_FILE, GDRIVE_BEAR_AND_TOKENS_FILE)
    #del img_uploader_first_config

    app = App()
    app.start()
    cam1_light_control = GpioLightingController.GpioLightingController(CAM1LIGHT_PIN)
    with PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, refresh_rate_seconds=1) as pir1thread:
        with PiCam.PiCameraRecorder(cam1_light_control, picture_scheme="../camera/mms", video_scheme="../camera/video0", subject=pir1thread, prio = 0, picture_timestamp=True, video_timestamp=True, rotation=180, timeout=RECORDING_TIME_SECONDS) as cam1, \
        GDriveImgUploader.GoogleDriveImageUploader(curl_like_object = curl, image_selector=img_selector, device_verif_filename=GDRIVE_DEV_VERIF_FILE, bearer_and_perm_tokens_filename=GDRIVE_BEAR_AND_TOKENS_FILE, prio=1, interface="ppp0", verbose=True, subject=pir1thread) as img_uploader:
            while not app.shutdown:
                app.run()
        pir1thread.join(RECORDING_TIME_SECONDS)
    
    app.stop()
    sys.exit(0)

