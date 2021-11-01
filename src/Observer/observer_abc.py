import abc

class AbstractObserver(object):
    __metaclass__ = abc.ABCMeta

    def update(self, value):
        pass

    @abc.abstractmethod
    def __enter__(self):
        return self
    
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        pass