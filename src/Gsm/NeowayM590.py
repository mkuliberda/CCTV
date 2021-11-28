import serial
from time import sleep
from Gsm import AbstractGsm as AbsGsm
from Observer import observer_abc as AbsObserver
import datetime

class M590(AbsGsm.AbstractGsm, AbsObserver.AbstractObserver):
    def __init__(self, subject, port, baudrate, rd_buffer_size=31):
        self._registered = False
        self._recipient = ""
        self._message = ""
        self._fatal_error_counter = 0
        self._is_sending = False
        self._subject = subject
        self._old_value = False
        self.open(port, baudrate, rd_buffer_size)
        if subject is not None:
            self._subject.attach(self)

    def set_msg_recipient(self, recipient):
        self._recipient = recipient

    def set_msg_text(self, text):
        self._message = text

    def get_datetime_string(self):
        dt_string = self.send_receive("at+cclk?\r")[10:27]
        try:
            return datetime.datetime.strptime(dt_string, "%y/%m/%d,%H:%M:%S")
        except ValueError as e:
            print(e)
            return None

    def open(self, port, baudrate, rd_buffer_size):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        sleep(1.0)
        self._rd_buffer_size = rd_buffer_size
        print("starting M590")
        self.clear_buffers()
        while self.send_command('ATE0\r') is False:
            print("Error setting echo off") #turn off echo
            self.clear_buffers()
        while self.send_command('AT+CMGF=1\r') is False: #set sms mode to text
             print("Error setting mode to text") 
             self.clear_buffers()
        while self.send_command('AT+CSCS=\"GSM\"\r') is False:
            print("Error setting character set")
            self.clear_buffers()
        while self.get_module_status() is "Ready":
            sleep(1)
        self._registered = self.get_registration_status()[0]
        print("started M590")
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self._subject is not None:
            self._subject.detach(self)
        self.ser.close()

    def clear_buffers(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        #while ">" in self.send_receive():
        #    print("> in buffer")
        #    self.ser.write([26])
        #    sleep(1)
        while self.send_command() is False:
            print("resetting buffer")
            sleep(1)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
    
    def reset_module(self):
        pass    

    def update(self, value):
        print("M590 update, registered:" + str(self.is_registered()) + ", sending sms:" + str(self._is_sending) + ", pir_value:" + str(value) + ", fatal counter: " + str(self._fatal_error_counter))
        if value != self._old_value:
            self._old_value = value
            if self._is_sending is False:
                if value is True and self._fatal_error_counter < 10:
                    while self.get_registration_status()[0] is False:
                        self.clear_buffers()
                    print(self.send_sms(self._recipient, self._message))
           
    def is_registered(self):
        return self._registered

    def close(self):
        self.ser.close()

    def send_command(self, command='AT\r'):
        self.ser.write(command.encode())
        try:
            data = self.ser.read(self._rd_buffer_size).decode()
            if "OK" in data:
                return True
            elif "ERROR" in data:
                print("Error, received", data, " after command: ", command)
                return False
            elif ">" in data:
                self.ser.write([26])
                return False
            else:
                print("Error, received ", data, " after command: ", command)
                return False
        except UnicodeDecodeError as e:
            print(e)
            return False

    def send_receive(self, cmd='AT\r'):
        self.ser.write(cmd.encode())
        return self._read_buffer()

    def get_signal_quality(self):
        data = self.send_receive('AT+CSQ\r')
        if "OK" not in data: return ["ERROR", -1, -1]
        data = data.split("\r\n")
        data=data[1].split(",")
        channel_bit_error_rate = int(data[1])
        data = data[0].split(": ")
        rssi = int(data[1])
        if rssi >= 22 and rssi < 28:
            signal_strength = "GOOD"
        elif rssi >= 28:
            signal_strength = "VERY GOOD"
        else:
            signal_strength = "WEAK"
        return [signal_strength, rssi, channel_bit_error_rate]

    def get_registration_status(self):
        data = self.send_receive('AT+CREG?\r')
        if "OK" not in data:
            return [False, "AT+CREG? error"]
        data = data.split('\r\n')
        data = data[1].split(',')
        try:
            if data[1] == '1':
                self._registered = True
                return [True, "Local"]
            if data[1] == '5':
                self._registered = True
                return [True, "Roaming"]
            else: 
                self._registered = False
                return [False, "Not registered or unknown"]
        except IndexError as e:
            return [False, "Unknown Error"]

    def get_module_status(self):
        status_dict = {0:"READY", 2:"UNKNOWN", 3:"RINGING", 4:"CALLING", 5:"ASLEEP"}
        data = self.send_receive('AT+CPAS\r')
        if "OK" not in data:
            return "ERROR\r\n"
        data = data.split('\r\n')
        data=int(data[1].split(': ')[1])
        return status_dict[data]
    
    def send_sms(self, recipient="", text="Empty message"):
        if len(recipient) is 0:
            self._fatal_error_counter+=1
            raise ValueError("Provide recipient phone number")
        self._is_sending = True       
        if ">" in self.send_receive('AT+CMGS=\"' + recipient + '\"\r'):
            print("sms sending...")
            self.ser.write(text.encode())
            self.ser.write([26])
            ret = self._read_buffer()
            if "ERROR" in ret:
                self.clear_buffers()
                self._fatal_error_counter+=1
            else:
                self._fatal_error_counter=0
            self._is_sending = False
            return ret
        else:
            print("sms not sending...")
            self._fatal_error_counter+=1
            ret = self._read_buffer()
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._is_sending = False
            return ret

    def _read_buffer(self):
        try:
            return self.ser.read(self._rd_buffer_size).decode()
        except UnicodeDecodeError:
            self.ser.reset_input_buffer()
            return "ERROR\r\n"


