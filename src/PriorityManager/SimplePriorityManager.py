from PriorityManager import AbstractPriorityManager as AbsPrioMgr

class SimplePriorityManager(AbsPrioMgr.AbstractPriorityManager):
    def __init__(self):
        self._priority = None

    def set_priority(self, prio):
        if type(prio) == int or type(prio) == float:
            self._priority = prio
        else:
            raise ValueError(f"{prio} is not a number, please use only int or float")

    def get_priority(self):
        return self._priority

    def print_priority(self):
        print(f"My priority is {self._priority}")