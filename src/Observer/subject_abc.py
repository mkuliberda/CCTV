import abc
from Observer import observer_abc as AbsObs

class AbstractSubject(object):
    __metaclass__ = abc.ABCMeta
    _observers = set()

    def attach(self, observer):
        if not isinstance(observer, AbsObs.AbstractObserver):
            raise TypeError("Incorrect type of argument. Should be of type AbstractObserver")
        self._observers.add(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, value=None):
        for observer in self._observers:
            if value == None:
                observer.update()
            else:
                observer.update(value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._observers.clear()