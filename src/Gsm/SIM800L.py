import serial
from time import sleep
from Gsm import AbstractGsm as AbsGsm
import RPi.GPIO as GPIO

class SIM800L(AbsGsm.AbstractGsm):
    def __init__(self, port, baudrate, rst_pin, rd_buffer_size=31):
        self._name = "SIM800L"
        self._rst_pin = rst_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._rst_pin, GPIO.OUT)
        GPIO.output(self._rst_pin, GPIO.HIGH)
        AbsGsm.AbstractGsm.__init__(self)
        self.open(port, baudrate, rd_buffer_size)

    def open(self, port, baudrate, rd_buffer_size):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        sleep(1.0)
        self._rd_buffer_size = rd_buffer_size
        print("starting SIM800L")
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
            sleep(1.0)
        while self._registered is False:
            [self._registered, state] = self.get_registration_status()
            print("Registration state is: ", state)
            sleep(1.0)
        self._registered = True
        print("started SIM800L")
    
    def clear_buffers(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        while self.send_command() is False and self._fatal_error_counter <= self._fatal_error_count_limit:
            print("resetting buffer, fatal_error_cnt: ", self._fatal_error_counter)
            sleep(2)
            self._fatal_error_counter += 1
        if(self._fatal_error_counter > self._fatal_error_count_limit):
            self.reset(type="HARD")
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()  

    # def update(self, value):
    #     print("SIM800L update, registered:" + str(self.is_registered()) + ", sending mms:" + str(self._is_sending) + ", pir_value:" + str(value) + ", fatal counter: " + str(self._fatal_error_counter))
    #     if value != self._old_value:
    #         self._old_value = value
    #         if self._is_sending is False:
    #             if value is True and self._fatal_error_counter < 10:
    #                 while self.get_registration_status()[0] is False:
    #                     self.clear_buffers()
    #                 if self._img_file_scheme is None:
    #                     raise FileNotFoundError
    #                 list_of_files = glob.glob(self._img_file_scheme)
    #                 newest_file = max(list_of_files, key=os.path.getctime)
    #                 print(self.send_mms(self._recipient, self._message, newest_file))
           
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
        if rssi == 0 or rssi == 1:
            signal_strength = "PERFECT"
        elif rssi >= 2 and rssi <= 30:
            signal_strength = "GOOD"
        elif rssi >= 31 and rssi <= 98:
            signal_strength = "WEAK"
        else:
            signal_strength = "NOT DETECTABLE"
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
            elif data[1] == '2':
                self._registered = True
                return [False, "SEARCHING"]
            elif data[1] == '5':
                self._registered = True
                return [True, "ROAMING"]
            else: 
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

    def send_mms(self, recipient, message, image_path):
        print("Recipient: ", recipient)
        print("Message: ", message)
        print("Image: ", image_path)
        print("MMS feature is not avbl on this machine yet")

    def reset(self, type):
        if type is "HARD":
            print("SIM800L hard reset")
            GPIO.output(self._rst_pin, GPIO.LOW)
            sleep(0.2)
            GPIO.output(self._rst_pin, GPIO.HIGH)
            sleep(10)
        self._fatal_error_counter = 0

        


