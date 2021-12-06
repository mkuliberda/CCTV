import abc
from datetime import datetime as dt


class AbstractGsm:
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self._registered = False
        self._recipient = ""
        self._message = ""
        self._fatal_error_counter = 0
        self._is_sending = False
        self._img_file_scheme = None

    @abc.abstractmethod
    def open(self, port, baudrate):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError

    @abc.abstractmethod
    def set_msg_recipient(self, recipient):
        self._recipient = recipient

    @abc.abstractmethod
    def set_msg_text(self, text):
        self._message = text

    @abc.abstractmethod
    def set_img_file_scheme(self, scheme):
        self._img_file_scheme = scheme

    @abc.abstractmethod
    def is_registered(self):
        return self._registered

    @abc.abstractmethod
    def send_sms(self, recipient, text):
        raise NotImplementedError

    @abc.abstractmethod
    def get_datetime_string(self):
        dt_string = self.send_receive("at+cclk?\r")[10:27]
        try:
            return dt.strptime(dt_string, "%y/%m/%d,%H:%M:%S")
        except ValueError as e:
            print(e)
            return None

    @abc.abstractmethod
    def send_mms(self, recipient, message, image_path):
        raise NotImplementedError