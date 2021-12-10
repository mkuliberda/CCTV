from CameraRecorder import PiCameraRecorder as PiCam
from MotionDetector import PIRMotionDetector as PIRSensor
from LightingController import GpioLightingController
from Utilities import Loop
from Gsm import MessageSender, SIM800L
import RPi.GPIO as GPIO
from datetime import datetime as dt


#import sys

# Pin control
PIRSENSOR1_PIN = 18
CAM1LIGHT_PIN = 23
SIM800L_RST_PIN = 24

# Serial settings
SERIAL0_BAUDRATE = 115200
SERIAL0_PORT = "/dev/ttyS0"
DATETIME_FORMAT = "%y%m%d%H%M%S"
RECORDING_TIME_SECONDS = 30

print(dt.now().strftime(DATETIME_FORMAT))

cam1_light_control = GpioLightingController.GpioLightingController(CAM1LIGHT_PIN)

with PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, refresh_rate_seconds=2) as pir1thread:
    with PiCam.PiCameraRecorder(cam1_light_control, picture_path="camera/mms", video_path="camera/video0", subject=pir1thread, picture_timestamp=True, video_timestamp=True, rotation=180, timeout=RECORDING_TIME_SECONDS) as cam1, \
        SIM800L.SIM800L(port=SERIAL0_PORT, baudrate=SERIAL0_BAUDRATE, rst_pin=SIM800L_RST_PIN) as sim800l:
        with MessageSender.MessageSender(subject=pir1thread, gsm_module=sim800l) as messenger1:
            messenger1.set_msg_recipient('+48506696574')
            messenger1.set_msg_text('Object detected')
            messenger1.set_img_file_scheme("camera/*.jpg")
            Loop.dockerized_run()  #change to dockerized_run when running as docker image
    pir1thread.join(RECORDING_TIME_SECONDS)

GPIO.cleanup()
#print(sys.path)
