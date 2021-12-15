import serial
from time import sleep
from Gsm import AbstractGsmDevice as AbsGsm

class M590(AbsGsm.AbstractGsmDevice):
    def __init__(self, port, baudrate, rd_buffer_size=31):
        self.model = "M590"
        self._rd_buffer_size = rd_buffer_size
        self._baudrate = baudrate
        AbsGsm.AbstractGsmDevice.__init__(self)
        self.ser = serial.Serial(port, self._baudrate, timeout=1)
        self.configure()

    def configure(self):
        sleep(1.0)
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
          
    def close(self):
        self.ser.close()

    def send_command(self, command='AT\r'):
        self.ser.write(command.encode(errors="ignore"))
        try:
            data = self.ser.read(self._rd_buffer_size).decode(errors="ignore")
            if "OK" in data:
                return True
            if "ERROR" in data:
                print("Error, received", data, " after command: ", command)
                return False
            if ">" in data:
                self.ser.write([26])
                return False
            print("Error, received ", data, " after command: ", command)
            return False
        except UnicodeDecodeError as e:
            print(e)
            return False

    def send_receive(self, cmd='AT\r'):
        self.ser.write(cmd.encode(errors="ignore"))
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
                return [True, "LOCAL"]
            if data[1] == '5':
                self._registered = True
                return [True, "ROAMING"]
            self._registered = False
            return [False, "NOT REGISTERED OR UNKNOWN"]
        except IndexError as e:
            return [False, e]

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
            self.fatal_error_counter+=1
            raise ValueError("Provide recipient phone number")
        self.is_sending = True       
        if ">" in self.send_receive('AT+CMGS=\"' + recipient + '\"\r'):
            print("sms sending...")
            self.ser.write(text.encode(errors="ignore"))
            self.ser.write([26])
            ret = self._read_buffer()
            if "ERROR" in ret:
                self.clear_buffers()
                self.fatal_error_counter+=1
            else:
                self.fatal_error_counter=0
            self.is_sending = False
            return ret
        else:
            print("sms not sending...")
            self.fatal_error_counter+=1
            ret = self._read_buffer()
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.is_sending = False
            return ret

    def _read_buffer(self):
        try:
            return self.ser.read(self._rd_buffer_size).decode(errors="ignore")
        except UnicodeDecodeError:
            self.ser.reset_input_buffer()
            return "ERROR\r\n"

    def send_mms(self, recipient, message, image_path):
        print("MMS feature is not avbl on this machine")

    def reset(self, tpe):
        self.send_command("at+cfun=16\r")


