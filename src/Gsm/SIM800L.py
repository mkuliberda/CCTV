import serial
from time import sleep
from Gsm import AbstractGsmDevice as AbsGsm
import RPi.GPIO as GPIO

class SIM800L(AbsGsm.AbstractGsmDevice):
    def __init__(self, port, baudrate, rst_pin, pwr_pin, rd_buffer_size=31):
        self.model = "SIM800L"
        self._rst_pin = rst_pin
        self._pwr_pin = pwr_pin
        self._rd_buffer_size = rd_buffer_size
        self._sms_max_resp_time_sec = 60
        self._buffer_read_timeout = 5
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._rst_pin, GPIO.OUT, initial=1)
        GPIO.setup(self._pwr_pin, GPIO.OUT, initial=0)
        AbsGsm.AbstractGsmDevice.__init__(self)
        self._baudrate = baudrate
        self.ser = serial.Serial(port, self._baudrate, timeout=self._buffer_read_timeout)
        self.configure()

    def configure(self):
        print("starting SIM800L")
        sleep(20)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.set_baudrate(self._baudrate)
        while self.send_command('ATE0\r') is False:
            print(self.model + ", Error setting echo off") #turn off echo
            self.clear_buffers()
        while self.send_command('AT+CMGF=1\r') is False: #set sms mode to text
             print(self.model + ", Error setting mode to text") 
             self.clear_buffers()
        while self.send_command('AT+CSCS=\"GSM\"\r') is False:
            print(self.model + ", Error setting character set")
            self.clear_buffers()
        while self.get_module_status() is "Ready":
            pass
        while self._registered is False:
            [self._registered, state] = self.get_registration_status()
            print(self.model + ", Registration state is: ", state)
        self._registered = True
        print("started SIM800L")
    
    def clear_buffers(self):
        #self.ser.reset_input_buffer()
        #self.ser.reset_output_buffer()
        while self.send_command() is False and self.fatal_error_counter <= self._fatal_error_count_limit:
            print(self.model + " resetting buffer, fatal_error_cnt: ", self.fatal_error_counter)
            self.fatal_error_counter += 1
        if self.fatal_error_counter > self._fatal_error_count_limit:
            self.reset(type="hard")
        #self.ser.reset_input_buffer()
        #self.ser.reset_output_buffer()  
           
    def close(self):
        self.ser.close()
        GPIO.output(self._pwr_pin, GPIO.HIGH)

    def send_command(self, command='AT\r'):
        self.ser.write(command.encode(errors="ignore"))
        try:
            data = self.ser.read(self._rd_buffer_size).decode()
            if "OK" in data:
                self.fatal_error_counter = 0
                return True
            elif "ERROR" in data:
                print(self.model + ", Error, received ", data, " after command: ", command)
                return False
            elif ">" in data:
                self.ser.write([26])
                return False
            elif len(data) is 0:
                self.ser.write("at\r".encode())
                self.ser.write([26])
                return False
            return False
        except UnicodeDecodeError as e:
            print(e)
            return False

    def send_receive(self, cmd='AT\r'):
        self.ser.write(cmd.encode())
        return self._read_buffer()

    def get_signal_quality(self):
        data = self.send_receive('AT+CSQ\r')
        if "OK" not in data:
            return ["ERROR", -1, -1]
        data = data.split("\r\n")
        data=data[1].split(",")
        channel_bit_error_rate = int(data[1])
        data = data[0].split(": ")
        rssi = int(data[1])
        if rssi == 0 or rssi == 1:
            signal_strength = "PERFECT"
        elif rssi >= 2 and rssi <= 30:
            signal_strength = "GOOD"
        elif rssi >= 31 and rssi <= 98:
            signal_strength = "WEAK"
        signal_strength = "NOT DETECTABLE"
        return [signal_strength, rssi, channel_bit_error_rate]

    def get_registration_status(self):
        data = self.send_receive('AT+CREG?\r')
        if "OK" not in data:
            return [False, self.model + ", AT+CREG? error"]
        data = data.split('\r\n')
        data = data[1].split(',')
        try:
            if data[1] == '1':
                self._registered = True
                self.fatal_error_counter = 0
                return [True, "LOCAL"]
            elif data[1] == '2':
                self.fatal_error_counter = 0
                self._registered = True
                return [False, "SEARCHING"]
            elif data[1] == '5':
                self.fatal_error_counter = 0
                self._registered = True
                return [True, "ROAMING"]
            self._registered = False
            return [False, "NOT REGISTERED OR UNKNOWN"]
        except IndexError as e:
            return [False, e]

    def get_module_status(self):
        status_dict = {0:"READY", 2:"UNKNOWN", 3:"RINGING", 4:"CALLING"}
        data = self.send_receive('AT+CPAS\r')
        if "OK" not in data:
            return "ERROR\r\n"
        data = data.split('\r\n')
        data=int(data[1].split(': ')[1])
        self.fatal_error_counter = 0
        return status_dict[data]
    
    def send_sms(self, recipient="", text="Empty message"):
        error_cnt=0
        rcv = ""
        if len(recipient) is 0:
            raise ValueError(self.model + ", Provide recipient phone number")
        self.is_sending = True
        rcv = self.send_receive('AT+CMGS=\"' + recipient + '\"\r')
        while len(rcv) and error_cnt < 5:
            rcv += self._read_buffer()
            error_cnt += 1
        if ">" in rcv:
            print(self.model + ", sms sending...")
            self.ser.write(text.encode())
            self.ser.write([26])
            ret = ""
            error_cnt = 0
            max_error_cnt = int(self._sms_max_resp_time_sec/self._buffer_read_timeout) + 1
            while "ERROR" not in ret and "CMGS" not in ret and error_cnt < max_error_cnt:
                ret += self._read_buffer()
                error_cnt += 1
                if "ERROR" in ret:
                    self.fatal_error_counter += 1
                elif "CMGS" in ret:
                    self.fatal_error_counter = 0
            self.is_sending = False
            return ret
        else:
            print(self.model + ", sms not sending...")
            self.fatal_error_counter+=1
            ret = self._read_buffer()
            self.is_sending = False
            return ret

    def _read_buffer(self):
        try:
            return self.ser.read(self._rd_buffer_size).decode()
        except UnicodeDecodeError:
            self.send_command()
            return "ERROR\r\n"

    def send_mms(self, recipient, message, image_path):
        print("Recipient: ", recipient)
        print("Message: ", message)
        print("Image: ", image_path)
        print("MMS feature is not avbl on this machine yet")

    def reset(self, type="hard"):
        if type is "hard":
            print(self.model + ", hard reset")
            GPIO.output(self._pwr_pin, GPIO.HIGH)
            sleep(1)
            GPIO.output(self._pwr_pin, GPIO.LOW)
            self.fatal_error_counter=0
            self.configure()

    def handle_error(self, err_type):
        print(self.model + ", error state")

    def set_baudrate(self, baudrate):
        self.send_command()
        ret = False
        while ret is False:
            print(self.model + ", setting baudrate: ", baudrate)
            ret = self.send_command("at+ipr=" + str(baudrate) + "\r")
        self.fatal_error_counter = 0
        return ret
        
        



