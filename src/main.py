from CameraRecorder import PiCameraRecorder as PiCam
from MotionDetector import PIRMotionDetector as PIRSensor
from LightingController import GpioLightingController
from Utilities import Loop, Clock
from Gsm import NeowayM590
import RPi.GPIO as GPIO


#import sys

# Pin control
PIRSENSOR1_PIN = 18
CAM1LIGHT_PIN = 23
M590_RING_PIN = 24

# Serial settings
SERIAL0_BAUDRATE = 9600
SERIAL0_PORT = "/dev/ttyS0"

GPIO.setmode(GPIO.BCM)

cam1_light_control = GpioLightingController.GpioLightingController(CAM1LIGHT_PIN)
with NeowayM590.M590(subject=None, port=SERIAL0_PORT, baudrate=SERIAL0_BAUDRATE) as clock_setter:
    Clock.set_system_clock(clock_setter.get_datetime_string())

with PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, refresh_rate_seconds=2) as pir1thread:
    with PiCam.PiCameraRecorder(cam1_light_control, picture_path="./camera/mms", video_path="./camera/video0", subject=pir1thread, video_timestamp=True, rotation=180, timeout=30) as cam1, \
        NeowayM590.M590(subject=pir1thread, port=SERIAL0_PORT, baudrate=SERIAL0_BAUDRATE) as messenger1:
        messenger1.set_msg_recipient('+48506696574')
        messenger1.set_msg_text('Object detected!')
        Loop.run()

GPIO.cleanup()
#print(sys.path)
