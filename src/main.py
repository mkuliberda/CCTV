from CameraRecorder import PiCameraRecorder as PiCam
from MotionDetector import PIRMotionDetector as PIRSensor
from LightingController import GpioLightingController
from Utilities import Loop
from Gsm import MessageSender, SIM800L
import RPi.GPIO as GPIO
from datetime import datetime as dt
import signal
import sys
from time import sleep
from Utilities import secrets


# Pin control
PIRSENSOR1_PIN = 18
CAM1LIGHT_PIN = 23
SIM800L_RST_PIN = 24
SIM800L_PWR_PIN = 25

# Serial settings
SERIAL0_BAUDRATE = 9600
SERIAL0_PORT = "/dev/ttyS0"
DATETIME_FORMAT = "%y%m%d%H%M%S"
RECORDING_TIME_SECONDS = 30

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
    print(dt.now().strftime(DATETIME_FORMAT))

    app = App()
    app.start()
    cam1_light_control = GpioLightingController.GpioLightingController(CAM1LIGHT_PIN)
    with PIRSensor.PIRMotionDetector(PIRSENSOR1_PIN, refresh_rate_seconds=1) as pir1thread:
        with SIM800L.SIM800L(port=SERIAL0_PORT, baudrate=SERIAL0_BAUDRATE, rst_pin=SIM800L_RST_PIN, pwr_pin=SIM800L_PWR_PIN) as sim800l, \
            PiCam.PiCameraRecorder(cam1_light_control, picture_path="camera/mms", video_path="camera/video0", subject=pir1thread, prio = 0, picture_timestamp=True, video_timestamp=True, rotation=180, timeout=RECORDING_TIME_SECONDS) as cam1, \
            MessageSender.MessageSender(subject=pir1thread, prio = 1, gsm_module=sim800l) as messenger1:
            messenger1.set_msg_recipient(secrets.get_phone_nbr()[0])
            messenger1.set_img_file_scheme("camera/*.jpg")
            while not app.shutdown:
                app.run()
        pir1thread.join(RECORDING_TIME_SECONDS)
    
    app.stop()
    sys.exit(0)

