import abc


class AbstractLightControl:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def turn_on(self):
        raise NotImplementedError

    @abc.abstractmethod
    def turn_off(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_state(self):
        raise NotImplementedError
