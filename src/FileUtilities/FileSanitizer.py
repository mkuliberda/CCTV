import glob
import threading

class FileSanitizer:
    def __init__(self, image_files_limit=100, video_files_limit=100):
        self._image_files_limit = image_files_limit
        self._video_files_limit = video_files_limit
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
       
    def run(self):
        if self.count_image_files() > self._image_files_limit or self.count_video_files() > self._video_files_limit:
            print("Image or video files limit reached")
            self.sanitize()

    def sanitize(self):
        pass

    def count_image_files(self, path="./camera/*.jpg"):
        print(len(glob.glob(path)))
        return len(glob.glob(path))

    def count_video_files(self, path="./camera/*.h264"):
        print(len(glob.glob(path)))
        return len(glob.glob(path))