import face_recognition
import cv2
from threading import Thread
from multiprocessing import Process
from shutil import move
from Observer import subject_abc as AbsSub
import time
import logging


class FaceImageExtractorProcess(Process):
    def __init__(self, file_selector, move_to_path=None, refresh_rate_seconds=1, file_converter=None):
        self._is_running = True
        self._refresh_rate_seconds = refresh_rate_seconds
        self._file_selector = file_selector
        self._file_converter = file_converter
        self._prev_file = None
        self._move_to_path = move_to_path
        self._is_analyzing = False
        self._blank_frame_counter = 0
        Process.__init__(self)
        self.start()


    #def terminate(self):
    #    self._is_running = False
        

    def run(self):
        while self._is_running:
            if self._is_analyzing is False:
                current_file = self._file_selector.get_file_relative_path()
                if current_file != self._prev_file and current_file is not None:
                    print("Face Extractor run on {}".format(current_file))
                    if self._file_converter is not None:
                        converted_file = self._file_converter.convert(current_file)
                    else:
                        converted_file = current_file
                    self.extract_from_video(converted_file)
                    self._prev_file = current_file
            time.sleep(self._refresh_rate_seconds)


    def extract_from_video(self, video_file):
        if video_file is not None:
            try:
                # Open video file
                cap = cv2.VideoCapture(video_file)
                face_locations = []
                self._is_analyzing = True
                self._blank_frame_counter=0
                while True:
                    try:
                        # Grab a single frame of video
                        ret, frame = cap.read()
                        print("Extractor read frame: {}, {}".format(ret,frame))
                        if ret is True:
                            self._blank_frame_counter=0
                        # Convert the image from BGR color (which OpenCV uses) to RGB   
                        # color (which face_recognition uses)
                        rgb_frame = frame[:, :, ::-1]
                        # Find all the faces in the current frame of video
                        face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=0, model="cnn")
                        faces_found_cnt = len(face_locations)
                        print("found {} face(s) in this photograph.".format(faces_found_cnt))
                        if faces_found_cnt > 0:
                            filename = self._file_selector.get_workdir() + "/face_" + video_file.split("/")[-1].split(".")[0] + '.jpg'
                            logging.info("found face, saving to {}...".format(filename))
                            cv2.imwrite(filename, frame)
                            if self._move_to_path is not None:
                                logging.info("moving file {} to {}".format(video_file, self._move_to_path + video_file.split("/")[-1]))
                                move(video_file, self._move_to_path + video_file.split("/")[-1])
                            break
                    except TypeError as e:
                        logging.error(e)
                        self._blank_frame_counter+=1
                        if self._blank_frame_counter > 10:
                            if self._move_to_path is not None:
                                logging.info("moving file {} to {}".format(video_file, self._move_to_path + video_file.split("/")[-1]))
                                move(video_file, self._move_to_path + video_file.split("/")[-1])
                            break
            except FileNotFoundError as e:
                logging.error(e)
            self._is_analyzing = False
            cap.release()


    #Context manager methods
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #self.terminate()
        self.kill()
