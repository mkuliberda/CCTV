import abc


class AbstractLightControl:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def turn_on(self):
        pass

    @abc.abstractmethod
    def turn_off(self):
        pass

    @abc.abstractmethod
    def get_state(self):
        pass
