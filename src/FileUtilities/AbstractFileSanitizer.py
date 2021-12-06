import abc


class AbstractFileSanitizer:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError
    
    def __enter__(self):
        return self

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError


