import glob
import threading

class FileSanitizer:
    def __init__(self, files_limit=100, filename_format="", path="", file_type=".jpg"):
        self._files_limit = files_limit
        self._file_type = file_type
        self._filename_format = filename_format
        self._path = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
       
    def run(self):
        #./camera/*.jpg
        if self.count_files(self._path + self._file_type) > self._files_limit:
            print("Image or video files limit reached")
            self.sanitize()

    def sanitize(self):
        pass

    def find_nearest(items, pivot):
        return min(items, key=lambda x: abs(x - pivot))

    def count_files(self, file_scheme):
        print(len(glob.glob(file_scheme)))
        return len(glob.glob(file_scheme))
