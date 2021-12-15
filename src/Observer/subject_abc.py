import abc
from Observer import observer_abc as AbsObs

class AbstractSubject:
    __metaclass__ = abc.ABCMeta
    _observers = []

    def attach(self, observer):
        if not isinstance(observer, AbsObs.AbstractObserver):
            raise TypeError("Incorrect type of argument. Should be of type AbstractObserver")
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, value=None):
        for observer in self._observers:
            if value is None:
                observer.update()
            else:
                observer.update(value)

    #Context manager methods
    def __enter__(self):
        return self

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError
        