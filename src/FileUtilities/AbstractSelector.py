import abc


class AbstractSelector:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_file_relative_path(self):
        raise NotImplementedError
    