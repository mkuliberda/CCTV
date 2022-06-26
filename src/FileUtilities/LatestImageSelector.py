#TODO: write this as a Producer to threaded queue
import os
import glob

class LatestImageSelector():
    def __init__(self, directory, img_file_type):
        self._img_file_type = img_file_type
        self._directory = directory


    def get_image_relative_path(self):
        list_of_files = glob.glob(self._directory + '/*.' + self._img_file_type)
        return max(list_of_files, key=os.path.getctime)
        #return "../camera/mms_220529123031.jpg"