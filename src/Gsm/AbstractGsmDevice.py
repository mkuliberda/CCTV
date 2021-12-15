import abc
from datetime import datetime as dt


class AbstractGsmDevice:
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self._registered = False
        self._recipient = ""
        self._message = ""
        self._fatal_error_count_limit = 5
        self.fatal_error_counter = 0
        self.error_handler = {
            "decoding": self.handle_decoding_error,
            "no_response": self.handle_no_response,
            "setting": self.handle_setting_error
            }
        self.error_counter = {
            "decoding": 0,
            "no_response": 0,
            "setting": 0
            }
        self._error_cnt_limit = {
            "decoding": 2,
            "no_response": 4,
            "setting": 5
        }
        self.is_sending = False
        self._img_file_scheme = None
        self._baudrate = 115200

    #Context manager methods
    def __enter__(self):
        return self
    
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        print("Gsm closing...")
        self.close()

    @abc.abstractmethod
    def configure(self):
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
    def set_error_count_limits(self, limits_dict):
        try:
            self._error_cnt_limit.baudrate = limits_dict["baudrate"]
            self._error_cnt_limit.no_response = limits_dict["no_response"]
            self._error_cnt_limit.setting = limits_dict["setting"]
        except KeyError as e:
            print(e + "Please provide dict in form of: {\"baudrate\": x, \"no_response\": y, \"setting\": z}")
    
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

    @abc.abstractmethod
    def reset(self, type):
        raise NotImplementedError
    
    @abc.abstractmethod
    def handle_decoding_error(self):
        raise NotImplementedError

    @abc.abstractmethod
    def handle_no_response(self):
        raise NotImplementedError

    @abc.abstractmethod
    def handle_setting_error(self):
        raise NotImplementedError

    @abc.abstractmethod
    def handle_error_state(self, err_type):
        self.error_handler[err_type]

    @abc.abstractmethod
    def set_baudrate(self, baudrate):
        raise NotImplementedError