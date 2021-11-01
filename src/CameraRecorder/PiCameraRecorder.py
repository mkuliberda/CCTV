import time
import datetime
from  picamera import PiCamera

class PiCameraRecorder():
    def record(video_path, timeout=10):
        now = datetime.datetime.now()
        camera = PiCamera()
        camera.rotation = 180
        
        camera.start_recording(video_path.split('/')[-1] + '_' + str(now.year) + str(now.month) + str(now.day)+ str(now.hour) + str(now.minute) + str(now.second) + '.h264')
        time.sleep(timeout)
        camera.stop_recording()