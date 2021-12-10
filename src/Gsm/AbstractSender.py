import abc


class AbstractSender:
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self._recipient = ""
        self._message = ""
        self._img_file_scheme = None

    #Context manager methods
    def __enter__(self):
        return self
    
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        print("Gsm closing...")
        self.close()

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
