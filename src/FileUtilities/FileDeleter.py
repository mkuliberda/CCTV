import glob
from FileUtilities import AbstractCleaner as AbsCleaner
import os
import logging
from time import sleep
from threading import Thread

class FileDeleter(AbsCleaner.AbstractCleaner):
    def __init__(self, file_type, files_limit=100, path=""):
        self._files_limit = files_limit
        self._file_type = file_type
        self._path = path

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run(self):
        while self.get_files_by_type(self._path, self._file_type)[1] > self._files_limit:
            oldest_file = min(self.get_files_by_type(self._path, self._file_type)[0], key=os.path.getctime)
            logging.info("Deleting oldest file:{}".format(oldest_file))
            os.remove(oldest_file)
 
    def get_files_by_type(self, path, tpe):
        list_of_files = glob.glob(path + '/*.' + tpe)
        return [list_of_files, len(list_of_files)]


class FileDeleterThreaded(AbsCleaner.AbstractCleaner, Thread):
    def __init__(self, file_type, files_limit=100, path=""):
        self._files_limit = files_limit
        self._file_type = file_type
        self._path = path
        self._is_running = True
        Thread.__init__(self)
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()

    def terminate(self):
        self._is_running = False

    def run(self):
        while self._is_running:
            while self.get_files_by_type(self._path, self._file_type)[1] > self._files_limit:
                try:
                    oldest_file = min(self.get_files_by_type(self._path, self._file_type)[0], key=os.path.getctime)
                    logging.info("Deleting oldest file:{}".format(oldest_file))
                    os.remove(oldest_file)
                except FileNotFoundError as e:
                    logging.error(e)
            sleep(1)
    
    def get_files_by_type(self, path, tpe):
        list_of_files = glob.glob(path + '/*.' + tpe)
        return [list_of_files, len(list_of_files)]

