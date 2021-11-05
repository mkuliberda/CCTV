from CameraRecorder import PiCameraRecorder as PiCam
from MotionDetector import PIRMotionDetector as PIRSensor
from LightingController import LightingController as LightCtrl
from Utilities import Loop
#import sys

# Pin control
PIRSENSOR1_PIN = 18
PIRSENSOR2_PIN = 19
CAM1LIGHT_PIN = 30


cam1 = PiCam.PiCameraRecorder("video0", timestamp=False, rotation=180)
cam1_light_control = LightCtrl.LightingController(CAM1LIGHT_PIN)
pir1thread = PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, 1)
pir1thread.attach(cam1_light_control)
pir1thread.attach(cam1)
pir1thread.start()

Loop.run()


pir1thread.terminate()
pir1thread.join()
pir1thread.detach(cam1)
pir1thread.detach(cam1_light_control)
cam1_light_control.turnOFF()



#print(sys.path)