import serial
from curses import ascii 
import time
import sys
from Gsm import AbstractGsm as AbsGsm

class M590(AbsGsm.AbstractGsm):

    def __init__(self):
        self._registered = False
        self._registration_status = "Not registered"
        self._rd_buffer_size = 1024

    def open(self, port, baudrate, rd_buffer_size=31):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self._rd_buffer_size = rd_buffer_size
        self.ser.flushInput()
        self.ser.flushOutput()
        self.send_command('ATE0\r') #turn off echo 
        self._registered = self.is_registered()

    def is_registered(self):
        self._registered = self.get_registration_status()[0]
        return self._registered

    def close(self):
        self.ser.close()

    def send_command(self, command):
        self.ser.write(command.encode())
        data = self.ser.read(self._rd_buffer_size).decode()
        if "OK\r\n" in data:
            return True
        if "ERROR" in data:
            print("Error ", data, " in command: ", command)
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
        if not self.send_command('AT+CMGF=1\r'): #set sms mode to text
            return "Error setting mode to text" 
        if not self.send_command('AT+CSCS=\"GSM\"\r'):
            return "Error setting character set" 
        if ">" in self.send_receive('AT+CMGS=\"' + recipient + '\"\r'):
            self.send_receive(text)
            self.ser.write([26])
            time.sleep(2)
            return self.ser.read(self._rd_buffer_size).decode()
        else:
            return self.send_receive()
