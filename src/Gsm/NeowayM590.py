import serial
import time
import sys
from Gsm import AbstractGsm as AbsGsm

class M590(AbsGsm.AbstractGsm):

    def __init__(self):
        self._registered = False

    def open(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.ser.flushInput()
        self.ser.flushOutput()
        self.send_command('ATE0\r'.encode()) #turn off echo 
        self.send_command('AT+CMGF=1\r'.encode()) #set sms mode to text
        self._registered = self.send_command('AT+CREG?\r'.encode()) 
        print(self._registered)

    def close(self):
        self.ser.close()

    def send_command(self, command):
        self.ser.write(command)
        data = self.ser.read(31).decode()
        if "OK\r\n" in data:
            return True
        if "ERROR" in data:
            print(data)
            return False

    def get_signal_quality(self):
        self.ser.write('AT+CSQ\r'.encode())
        data = self.ser.read(31).decode()
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
