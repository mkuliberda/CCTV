from abc import ABC, abstractmethod


class AbstractPriorityManager(ABC):

    @abstractmethod
    def set_priority(self, prio):
        raise NotImplementedError

    @abstractmethod                
    def get_priority(self):
        raise NotImplementedError
      
    @abstractmethod
    def print_priority(self):
        raise NotImplementedError
