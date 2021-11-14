import abc


class AbstractGsm:
    __metaclass__ = abc.ABCMeta
 
    @abc.abstractmethod
    def open(self, port, baudrate):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError

    @abc.abstractmethod
    def read_all_sms(self):
        raise NotImplementedError

    @abc.abstractmethod
    def send_sms(self, recipient, text):
        raise NotImplementedError
