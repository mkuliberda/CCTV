from CameraRecorder import PiCameraRecorder as PiCam
import sys
import time
from MotionDetector import PIRMotionDetector as PIRSensor

# Pin control
PIRSENSOR1_PIN = 18
PIRSENSOR2_PIN = 19

print("main")

cam1 = PiCam.PiCameraRecorder()
pir1thread = PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN,1)
pir1thread.start()

time.sleep(5)

pir1thread.terminate()
pir1thread.join(30)


#print(sys.path)