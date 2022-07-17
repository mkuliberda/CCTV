import subprocess
from os import remove
import logging


class VideoConverterffmpeg():
    def __init__(self, target_format:str, src_framerate:int=25, rm_src_file:bool=True):
        self._target_format = target_format
        self._src_framerate = src_framerate
        self._rm_src_file = rm_src_file


    def convert(self, file_to_convert):
        try:
            print("converting{} to {}...".format(file_to_convert, self._target_format))
            new_file = file_to_convert.replace("h264","mp4")
            subprocess.call(["ffmpeg -i " + file_to_convert + " -filter:v fps=" + str(self._src_framerate) + " " + new_file], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if self._rm_src_file:
                remove(file_to_convert)
            print("converter:{}".format(new_file))
            return new_file
        except FileNotFoundError as e:
            logging.error(e)
            return None
            