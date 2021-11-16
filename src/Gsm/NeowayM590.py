import serial
from curses import ascii 
import time
import sys
from Gsm import AbstractGsm as AbsGsm
from Observer import observer_abc as AbsObserver
from threading import Thread

class M590MessageSender(AbsGsm.AbstractGsm, AbsObserver.AbstractObserver):
    def __init__(self, subject, recipient, message, port, baudrate, rd_buffer_size=31):
        self._registered = False
        self._registration_status = "Not registered"
        self._rd_buffer_size = 1024
        self._recipient = recipient
        self._is_sending = False
        self._message = message
        self._subject = subject
        self._old_value = False
        self.open(port, baudrate, rd_buffer_size)
        self._subject.attach(self)

    def open(self, port, baudrate, rd_buffer_size=31):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self._rd_buffer_size = rd_buffer_size
        self.ser.flushInput()
        self.ser.flushOutput()
        self.send_command('ATE0\r') #turn off echo 
        if not self.send_command('AT+CMGF=1\r'): #set sms mode to 
            return "Error setting mode to text" 
        if not self.send_command('AT+CSCS=\"GSM\"\r'):
            return "Error setting character set" 

        self._registered = self.get_registration_status()[0]

    #def __del__(self):
        #self.ser.close()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._subject.detach(self)
        self.ser.close()

    def update(self, value):
        print("M590 update: ", self.is_registered(), self._is_sending, value)
        if value != self._old_value:
            self._old_value = value
            if self.is_registered() and self._is_sending is False and value is True:
                self._is_sending = True
                print(self.send_sms(self._recipient, self._message))
           
    def is_registered(self):
        return self._registered

    def close(self):
        self.ser.close()

    def send_command(self, command='AT\r'):
        self.ser.write(command.encode())
        data = self.ser.read(self._rd_buffer_size).decode()
        if "OK\r\n" in data:
            return True
        if "ERROR" in data:
            print("Error ", data, " in command: ", command)
            return False
        else:
            return False

    def send_receive(self, cmd='AT\r'):
        self.ser.write(cmd.encode())
        return self.ser.read(self._rd_buffer_size).decode()

    def get_signal_quality(self):
        data = self.send_receive('AT+CSQ\r')
        if "OK\r\n" not in data: return [-1, -1, -1]
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
        if "OK\r\n" not in data: return [-1, -1, -1]
        data = data.split('\r\n')
        data = data[1].split(',')
        if data[1] == '1':
            return [True, "Local"]
        if data[1] == '5':
            return [True, "Roaming"]
        else: 
            return [False, "Not registered or unknown"]

    def get_module_status(self):
        status_dict = {0:"READY", 2:"UNKNOWN", 3:"RINGING", 4:"CALLING", 5:"ASLEEP"}
        data = self.send_receive('AT+CPAS\r')
        if "OK\r\n" not in data: return [-1, -1, -1]
        data = data.split('\r\n')
        data=int(data[1].split(': ')[1])
        return status_dict[data]
    
    def send_sms(self, recipient="", text=""):
        self.ser.flushInput()
        self.ser.flushOutput()
        if self.send_command() is True:
            self.ser.flushInput()
            self.ser.flushOutput()
            if ">" in self.send_receive('AT+CMGS=\"' + recipient + '\"\r'):
                self.send_receive(text)
                self.ser.write([26])
                #time.sleep(2)
                ret = self.ser.read(self._rd_buffer_size).decode()
                self._is_sending = False
                return ret
            else:
                #time.sleep(2)
                #self._is_sending = False
                #self.ser.write([26])
                #return self.send_receive()
                ret = self.ser.read(self._rd_buffer_size).decode()
                self._is_sending = False
                return ret

