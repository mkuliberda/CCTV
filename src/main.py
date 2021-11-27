from CameraRecorder import PiCameraRecorder as PiCam
from MotionDetector import PIRMotionDetector as PIRSensor
from LightingController import GpioLightingController
from Utilities import Loop
from Gsm import NeowayM590
import RPi.GPIO as GPIO


#import sys

# Pin control
PIRSENSOR1_PIN = 18
CAM1LIGHT_PIN = 23
M590_RING_PIN = 24

GPIO.setmode(GPIO.BCM)

cam1_light_control = GpioLightingController.GpioLightingController(CAM1LIGHT_PIN)

with PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, 1) as pir1thread:
    with PiCam.PiCameraRecorder(cam1_light_control, picture_path="./camera/mms", video_path="./camera/video0", subject=pir1thread, video_timestamp=True, rotation=180, timeout=30) as cam1, \
        NeowayM590.M590(subject = pir1thread, recipient='+48506696574', message='Object detected!', port="/dev/ttyS0", baudrate=9600) as messenger1:
        Loop.run()

GPIO.cleanup()
#print(sys.path)
