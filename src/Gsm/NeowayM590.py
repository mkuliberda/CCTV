import serial
from curses import ascii 
import time
import sys
from Gsm import AbstractGsm as AbsGsm
from Observer import observer_abc as AbsObserver
from threading import Thread

class M590(AbsGsm.AbstractGsm, AbsObserver.AbstractObserver):
    def __init__(self, subject, recipient, message, port, baudrate, rd_buffer_size=31):
        self._registered = False
        self._registration_status = "Not registered"
        #self._rd_buffer_size = rd_buffer_size
        self._recipient = recipient
        self._is_sending = False
        self._message = message
        self._subject = subject
        self._old_value = False
        self.open(port, baudrate, rd_buffer_size)
        self._subject.attach(self)

    def open(self, port, baudrate, rd_buffer_size):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self._rd_buffer_size = rd_buffer_size
        print("starting M590")
        self.reset_buffer()
        while self.send_command('ATE0\r') is False:
            print("Error setting echo off") #turn off echo
            self.reset_buffer()
        while self.send_command('AT+CMGF=1\r') is False: #set sms mode to text
             print("Error setting mode to text") 
             self.reset_buffer()
        while self.send_command('AT+CSCS=\"GSM\"\r') is False:
            print("Error setting character set")
            self.reset_buffer()
        self._registered = self.get_registration_status()[0]
        print("started M590")
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._subject.detach(self)
        self.ser.close()

    def reset_buffer(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        while self.send_command() is False:
            print("resetting buffer")
            self.ser.write([26])
            time.sleep(2)

    def update(self, value):
        print("M590 update, registered:" + str(self.is_registered()) + ", sending sms:" + str(self._is_sending) + ", pir_value:" + str(value))
        if self._is_sending is False and value != self._old_value:
            self._old_value = value
            if value is True:
                while self.get_registration_status()[0] is False:
                    self.reset_buffer()
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
                print("Error ", data, " in command: ", command)
                return False
            else:
                return False
        except UnicodeDecodeError as e:
            print(e)
            return False

    def send_receive(self, cmd='AT\r'):
        self.ser.write(cmd.encode())
        try:
            return self.ser.read(self._rd_buffer_size).decode()
        except UnicodeDecodeError as e:
            print(e)
            return "Error\r"

    def get_signal_quality(self):
        data = self.send_receive('AT+CSQ\r')
        if "OK\r\n" not in data: return ["Error", -1, -1]
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
            return [-1, -1, -1]
        data = data.split('\r\n')
        data=int(data[1].split(': ')[1])
        return status_dict[data]
    
    def send_sms(self, recipient="", text=""):
        self._is_sending = True
        if len(recipient) is 0:
            raise ValueError("Provide recipient phone number")        
        self.ser.flushInput()
        self.ser.flushOutput()
        if ">" in self.send_receive('AT+CMGS=\"' + recipient + '\"\r'):
            print("sms sending...")
            self.ser.write(text.encode())
            self.ser.write([26])
            ret = self.ser.read(self._rd_buffer_size).decode()
            self.ser.flushInput()
            self.ser.flushOutput()
            self._is_sending = False
            return ret
        else:
            print("sms not sending...")
            ret = self.ser.read(self._rd_buffer_size).decode()
            self.ser.flushInput()
            self.ser.flushOutput()
            self._is_sending = False
            return ret


