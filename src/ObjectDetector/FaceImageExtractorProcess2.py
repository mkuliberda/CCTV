import cv2
from multiprocessing import Process
from shutil import move
import time
import logging


class FaceImageExtractorProcess(Process):
    def __init__(self, file_selector, haar_cascade_settings_file, move_to_path=None, refresh_rate_seconds=1, file_converter=None):
        self._is_running = True
        self._refresh_rate_seconds = refresh_rate_seconds
        self._file_selector = file_selector
        self._file_converter = file_converter
        self._prev_file = None
        self._move_to_path = move_to_path
        self._is_analyzing = False
        self._blank_frame_counter = 0
        self._haar_cascade_settings_file = haar_cascade_settings_file
        Process.__init__(self)
        self.start()


    #def terminate(self):
    #    self._is_running = False
        

    def run(self):
        while self._is_running:
            if self._is_analyzing is False:
                current_file = self._file_selector.get_file_relative_path()
                if current_file != self._prev_file and current_file is not None:
                    logging.info("Extracting from {}".format(current_file))
                    if self.extract_from_video(current_file) is True:
                        if self._file_converter is not None:
                            converted_file = self._file_converter.convert(current_file)
                        else:
                            converted_file = current_file
                        if self._move_to_path is not None:
                            logging.info("Moving file {} to {}".format(converted_file, self._move_to_path + converted_file.split("/")[-1]))
                            move(converted_file, self._move_to_path + converted_file.split("/")[-1])
                    else:
                        self._file_converter.convert(current_file)
                    self._prev_file = current_file
            time.sleep(self._refresh_rate_seconds)


    def extract_from_video(self, video_file):
        if video_file is not None:
            try:
                self._is_analyzing = True
                face_cascade = cv2.CascadeClassifier(self._haar_cascade_settings_file)
                video_capture = cv2.VideoCapture(video_file)
                num_faces = 0
                while True:
                    ret, frame = video_capture.read()
                    
                    if not ret:
                        break

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(
                        gray,
                        scaleFactor = 1.2,
                        minNeighbors = 5,
                        minSize = (30,30)
                        )

                    num_faces = len(faces)
                    if num_faces > 0:
                        filename = self._file_selector.get_workdir() + "/face_" + video_file.split("/")[-1].split(".")[0] + '.jpg'
                        logging.info("Found face, saving to {}...".format(filename))
                        cv2.imwrite(filename, frame)
                        break
            except FileNotFoundError as e:
                logging.error(e)
            self._is_analyzing = False
            video_capture.release()
            return num_faces > 0


    #Context manager methods
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #self.terminate()
        self.kill()
