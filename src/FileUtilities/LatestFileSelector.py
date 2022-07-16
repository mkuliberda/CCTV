import os
import glob
from FileUtilities import AbstractSelector as AbsSelector

class LatestFileSelector(AbsSelector.AbstractSelector):
    def __init__(self, workdir:str, file_extension:str=""):
        if len(file_extension) < 1:
            print ("Please provide file extension as string without dot e.g. \"xxx\"")
            raise ValueError
        self._file_extension = file_extension
        self._workdir = workdir

    def get_file_relative_path(self):
        try:
            list_of_files = glob.glob(self._workdir + '*.' + self._file_extension)
            return max(list_of_files, key=os.path.getctime)
        except ValueError:
            return None

    def get_workdir(self):
        return self._workdir
