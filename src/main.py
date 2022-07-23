from CameraRecorder.PiCameraRecorder import PiCameraRecorder as PiCam
from MotionDetector.PIRMotionDetector import PIRMotionDetector as PIRSensor
from LightingController.GpioLightingController import GpioLightingController
from Utilities import Loop
import RPi.GPIO as GPIO
from datetime import datetime as dt
import signal
import sys
import os
from time import sleep
from Utilities import secrets
from FileUtilities.LatestFileSelector import LatestFileSelector
from FileUtilities.FileDeleter import FileDeleterThreaded as FileDeleter
from FileUtilities.VideoConverter import VideoConverterffmpeg as VideoConverter
from FileUploaders.GoogleDriveImageUploaderProcess import GoogleDriveImageUploaderProcess as GDriveImageUploader
import pycurl
from ObjectDetector.HaarCascadeFaceImageExtractorProcess import HaarCascadeFaceImageExtractorProcess as FaceExtractor
import logging


logging.basicConfig(filename='../logs/cctv_{}.log'.format(dt.now().strftime("%y%m%d%H%M%S")), filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s', level=logging.INFO)
logging.info("CCTV starting...")

# Pin control
PIRSENSOR1_PIN = 18
CAM1LIGHT_PIN = 21

# General settings
DATETIME_FORMAT = "%y%m%d%H%M%S"
RECORDING_TIME_SECONDS = 30
GDRIVE_DEV_VERIF_FILE = "device_verif.json"
GDRIVE_BEAR_AND_TOKENS_FILE = "bearer_and_perm_tokens.json"
RECORDING_FRAMERATE = 10

class App:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print(flush=True)
        print('Received {}'.format("shutdown signal, exiting... please wait" if signum==2 else signum))
        logging.info("CCTV shutting down...")
        self.shutdown = True

    def start(self):
        print("App starting")

    def run(self):
        sleep(0.1)

    def stop(self):
        print(flush=True)
        GPIO.cleanup()

if __name__ == '__main__':

    curl = pycurl.Curl()
    jpg_selector = LatestFileSelector("../camera/recordings/", "jpg")
    h264_selector = LatestFileSelector("../camera/recordings/", "h264")
    video_converter_mp4 = VideoConverter(target_format="mp4", src_framerate=RECORDING_FRAMERATE)
    #img_uploader_first_config = GDriveImgUploader.GoogleDriveImageUploader(curl_like_object = curl, image_selector=None, device_verif_filename="device_verif.json", bearer_and_perm_tokens_filename="bearer_and_perm_tokens.json", prio=1, interface="eth0", verbose=True)
    #img_uploader_first_config.first_run(GDRIVE_DEV_VERIF_FILE, GDRIVE_BEAR_AND_TOKENS_FILE)
    #del img_uploader_first_config


    app = App()
    app.start()
    cam1_light_control = GpioLightingController(CAM1LIGHT_PIN)
    with FaceExtractor(file_selector=h264_selector, haar_cascade_settings_file="haarcascade_frontalface_default.xml", move_to_path="../camera/recordings/detections/", file_converter=video_converter_mp4) as face_extractor_process, \
        GDriveImageUploader(curl_like_object=curl, file_selector=jpg_selector, device_verif_filename=GDRIVE_DEV_VERIF_FILE, bearer_and_perm_tokens_filename=GDRIVE_BEAR_AND_TOKENS_FILE, interface="ppp0", verbose=True, move_to_path="../camera/recordings/uploaded/") as file_uploader, \
        FileDeleter(file_type="mp4", files_limit=1000, path="../camera/recordings/detections/") as detections_cleaner, \
        FileDeleter(file_type="mp4", files_limit=100, path="../camera/recordings/") as mp4_cleaner, \
        FileDeleter(file_type="jpg", files_limit=1000, path="../camera/recordings/uploaded/") as jpg_cleaner:
        with PIRSensor(PIRSENSOR1_PIN, refresh_rate_seconds=1) as pir1_thread:
            with PiCam(files_path="../camera/", lgt_ctrl=cam1_light_control, picture_prefix=None, video_prefix="video0_", subject=pir1_thread, prio = 0, picture_timestamp=True, video_timestamp=True, rotation=180, framerate=RECORDING_FRAMERATE, resolution=(640, 480), timeout=RECORDING_TIME_SECONDS) as cam1:
                while not app.shutdown:
                    app.run()
            pir1_thread.join(RECORDING_TIME_SECONDS)
        if file_uploader.get_uploading_state():
            file_uploader.join(5*60)
        else:
            file_uploader.join(1)
        detections_cleaner.join(5)
        mp4_cleaner.join(5)
        jpg_cleaner.join(5)
    
    app.stop()
    sys.exit(0)

