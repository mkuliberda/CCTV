#TODO: write this as a Producer to threaded queue
import os
import glob
from FileUtilities import AbstractSelector as AbsSelector

class LatestArchiveSelector(AbsSelector.AbstractSelector):
    def __init__(self, directory, file_type):
        self._archive_file_type = file_type
        self._directory = directory


    def get_file_relative_path(self):
        try:
            list_of_files = glob.glob(self._directory + '/*.' + self._archive_file_type)
            return max(list_of_files, key=os.path.getctime)
        except ValueError:
            return None
      