import face_recognition
import cv2
from threading import Thread
from multiprocessing import Process
from datetime import datetime as dt
from shutil import move
from Observer import subject_abc as AbsSub
import time


class FaceImageExtractorProcess(Process):
    def __init__(self, file_selector, move_to_path=None, refresh_rate_seconds=1):
        self._is_running = True
        self._refresh_rate_seconds = refresh_rate_seconds
        self._file_selector = file_selector
        self._prev_file = None
        self._move_to_path = move_to_path
        self._is_analyzing = False
        Process.__init__(self)
        self.start()


    #def terminate(self):
    #    self._is_running = False
        

    def run(self):
        while self._is_running:
            if self._is_analyzing is False:
                current_file = self._file_selector.get_file_relative_path()
                if current_file != self._prev_file and current_file is not None:
                    time.sleep(3) #TODO: check if this workaround can be solved Moov Atom Not Found" Error
                    self.extract_from_video(current_file)
                    self._prev_file = current_file
            time.sleep(self._refresh_rate_seconds)


    def extract_from_video(self, video_file):
        # Open video file
        print("Face Extractor run on {}".format(video_file))
        cap = cv2.VideoCapture(video_file)
        face_locations = []
        self._is_analyzing = True
        while True:
            try:
                # Grab a single frame of video
                ret, frame = cap.read()
                # Convert the image from BGR color (which OpenCV uses) to RGB   
                # color (which face_recognition uses)
                rgb_frame = frame[:, :, ::-1]
                # Find all the faces in the current frame of video
                face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=0, model="cnn")
                faces_found_cnt = len(face_locations)
                print("it's {}, I found {} face(s) in this photograph.".format(dt.now().strftime("%H:%M:%S"), faces_found_cnt))
                if faces_found_cnt > 0:
                    filename = self._file_selector.get_workdir() + "/face_" + video_file.split("/")[-1].split(".")[0] + '.jpg'
                    print(filename)
                    cv2.imwrite(filename, frame)
                    if self._move_to_path is not None:
                        move(video_file, self._move_to_path + video_file.split("/")[-1])
                    self._is_analyzing = False
                    break
            except TypeError:
                if self._move_to_path is not None:
                    move(video_file, self._move_to_path + video_file.split("/")[-1])
                self._is_analyzing = False
                break
        cap.release()


    #Context manager methods
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #self.terminate()
        self.kill()
