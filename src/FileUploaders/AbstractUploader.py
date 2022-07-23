import abc


class AbstractUploader:
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        pass

    #Context manager methods
    def __enter__(self):
        return self
    
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        pass
