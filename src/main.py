from CameraRecorder import PiCameraRecorder as PiCam
from MotionDetector import PIRMotionDetector as PIRSensor
from LightingController import GpioLightingController
from Utilities import Loop
#import sys

# Pin control
PIRSENSOR1_PIN = 18
PIRSENSOR2_PIN = 19
CAM1LIGHT_PIN = 30


cam1_light_control = GpioLightingController.GpioLightingController(CAM1LIGHT_PIN)

with PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, 1) as pir1thread:
    with PiCam.PiCameraRecorder(cam1_light_control, "video0", subject=pir1thread, timestamp=False, rotation=180, timeout=30):
        Loop.run()


#print(sys.path)
