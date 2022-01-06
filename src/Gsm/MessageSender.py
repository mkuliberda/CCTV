from time import sleep
from Observer import observer_abc as AbsObserver
from Gsm import AbstractSender as AbsSender
import glob
import os
from PriorityManager import SimplePriorityManager as PrioMgr


class MessageSender(AbsObserver.AbstractObserver, AbsSender.AbstractSender, PrioMgr.SimplePriorityManager):
    def __init__(self, subject, prio, gsm_module, sender_type="sms"):
        PrioMgr.SimplePriorityManager.__init__(self)
        self.set_priority(prio)
        self._gsm_module = gsm_module
        self._subject = subject
        self._sender_type = sender_type
        self._old_value = False
        if subject is not None:
            self._subject.attach(self)
        AbsSender.AbstractSender.__init__(self)
        
    def __exit__(self, exc_type, exc_value, traceback):
        if self._subject is not None:
            self._subject.detach(self)

    def find_newest_image_file(self):
        list_of_files = glob.glob(self._img_file_scheme)
        return max(list_of_files, key=os.path.getctime)

    def update(self, value):
        print(str(self._gsm_module.model) + \
            " update, registered:" + \
                str(self._gsm_module.is_registered()) + \
                    ", sending:" + str(self._gsm_module.is_sending) + \
                        ", pir_value:" + str(value) + \
                            ", fatal counter: " + str(self._gsm_module.fatal_error_counter))
           
        if value != self._old_value:
            self._old_value = value
            if self._gsm_module.fatal_error_counter > self._gsm_module.fatal_error_count_limit:
                self._gsm_module.reset()
            if self._gsm_module.is_sending is False:
                if value is True:
                    while self._gsm_module.get_registration_status()[0] is False:
                        self._gsm_module.clear_buffers()
                    if self._sender_type is "sms":
                        print(self._gsm_module.send_sms(self._recipient, self.find_newest_image_file().split("/")[1].split(".")[0].split("_")[1]))
                    elif self._sender_type is "mms":
                        if self._img_file_scheme is None:
                            raise FileNotFoundError
                        newest_file = self.find_newest_image_file()
                        print(self._gsm_module.send_mms(
                            self._recipient, newest_file.split("/")[1].split(".")[0].split("_")[1], newest_file))
    



