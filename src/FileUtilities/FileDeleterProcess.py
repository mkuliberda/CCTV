import glob
from FileUtilities import AbstractCleaner as AbsCleaner
import os
from multiprocessing import Process

class FileDeleterProcess(AbsCleaner.AbstractCleaner, Process):
    def __init__(self, file_type, files_limit=100, path=""):
        self._files_limit = files_limit
        self._file_type = file_type
        self._path = path
        Process.__init__(self)
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.kill()

    def run(self):
        while self.get_files_by_type(self._path, self._file_type)[1] > self._files_limit:
            print("Files limit reached")
            oldest_file = min(self.get_files_by_type(self._path, self._file_type)[0], key=os.path.getctime)
            print("Deleting oldest file:{}".format(oldest_file))
            os.remove(oldest_file)
 
    def get_files_by_type(self, path, tpe):
        list_of_files = glob.glob(path + '/*.' + tpe)
        return [list_of_files, len(list_of_files)]
