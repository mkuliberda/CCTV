from time import sleep
from Observer import observer_abc as AbsObserver
from Gsm import AbstractSender as AbsSender
import glob
import os


class MessageSender(AbsObserver.AbstractObserver, AbsSender.AbstractSender):
    def __init__(self, subject, gsm_module, sender_type="sms"):
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
            
    def update(self, value):
        print(str(self._gsm_module._name) + \
            " update, registered:" + \
                str(self._gsm_module.is_registered()) + \
                    ", sending:" + str(self._gsm_module._is_sending) + \
                        ", pir_value:" + str(value) + \
                            ", fatal counter: " + str(self._gsm_module._fatal_error_counter))
           
        if value != self._old_value:
            self._old_value = value
            if self._gsm_module._fatal_error_counter > self._gsm_module._fatal_error_count_limit:
                self._gsm_module.reset()
            if self._gsm_module._is_sending is False:
                if value is True:
                    while self._gsm_module.get_registration_status()[0] is False:
                        self._gsm_module.clear_buffers()
                    if self._sender_type is "sms":
                        print(self._gsm_module.send_sms(self._recipient, self._message))
                    elif self._sender_type is "mms":
                        if self._img_file_scheme is None:
                            raise FileNotFoundError
                        list_of_files = glob.glob(self._img_file_scheme)
                        newest_file = max(list_of_files, key=os.path.getctime)
                        print(self._gsm_module.send_mms(self._recipient, self._message, newest_file))





