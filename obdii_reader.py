from multiprocessing import Process, Event
import queue as Q
import time
import random
import RPi.GPIO as GPIO
import can
import time
import os
import queue
import csv
from datetime import datetime
from threading import Thread
led = 22
try:
    import serial
except:
    print("serial library not found. Continuing.")

try:
    import busio
except:
    print("busio library not found. Continuing.")

try:
    import can
except:
    print("can library not found. Continuing.")

try:
    import board
except:
    print("board library not found. Continuing.")

try:
    import RPi.GPIO as GPIO
except:
    print("RPi.GPIO library not found. Continuing.")

# Constants
ENGINE_COOLANT_TEMP = 0x05
ENGINE_RPM          = 0x0C
VEHICLE_SPEED       = 0x0D
MAF_SENSOR          = 0x10
O2_VOLTAGE          = 0x14
THROTTLE            = 0x11

PID_REQUEST         = 0x7DF
PID_REPLY           = 0x7E8

class ObdiiReader(Process):

    def __init__(self, queue, log_file_path, test=False):
        super(Process, self).__init__()
        self.queue = queue
        self.test = test
        self.exit = Event()

        self.speed = 0
        self.rpm = 0
        self.throttle = 0
        self.coolant_temp = 0

        self.log_file_path = log_file_path

        if not test:
            self._setup_obdii()
        self.last_timestamp = time.monotonic()

    def _setup_obdii(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(led,GPIO.OUT)
        GPIO.output(led,True)

        print('\n\rCAN Rx test')
        print('Bring up CAN0....')

        # Bring up can0 interface at 500kbps
        os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
        time.sleep(0.1)
        print('Ready')

        try:
            self.bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
        except OSError:
            print('Cannot find PiCAN board.')
            GPIO.output(led,False)
            exit(1)



    def run(self):
        print("Running GPS Reader")

        with open(self.log_file_path, "w") as log_file:
            self.csv_writer = csv.writer(log_file)
            self.csv_writer.writerow(["Speed", "RPM", "Throttle", "Coolant Temp"])

            while not self.exit.is_set():
                if not self.test:
                    self._update_stats()
                else:
                    self._update_fake_stats()

                self._log_stats()
                time.sleep(0.1)


    def _log_stats(self):
        stats = [
            self.speed,
            self.rpm,
            self.throttle,
            self.coolant_temp]
        self.csv_writer.writerow(stats)

        try:
            self.queue.put(stats, True, 0.1)
        except Q.Full:
            pass #Don't let a full queue cause an issue


    def _update_stats(self):
        self._get_coolant_temp()
        self._get_engine_rpm()
        self._get_speed()
        self._get_throttle()

    def _get_coolant_temp(self):
        GPIO.output(led,True)
        # Sent a Engine coolant temperature request
        msg = can.Message(arbitration_id=PID_REQUEST,
                data=[0x02,0x01,ENGINE_COOLANT_TEMP,0x00,0x00,0x00,0x00,0x00],
                extended_id=False)
        self.bus.send(msg)
        GPIO.output(led,False)

        # listen for response
        message = self.bus.recv()
        if message.arbitration_id == PID_REPLY and message.data[2] == ENGINE_COOLANT_TEMP:
            #Convert data into temperature in degrees F
            self.temperature = ((message.data[3] - 40)*(9/5))+32

    def _get_engine_rpm(self):
        GPIO.output(led,True)
        # Sent a Engine RPM request
        msg = can.Message(arbitration_id=PID_REQUEST,
                data=[0x02,0x01,ENGINE_RPM,0x00,0x00,0x00,0x00,0x00],
                extended_id=False)
        self.bus.send(msg)
        GPIO.output(led,False)

        # listen for response
        message = self.bus.recv()
        if message.arbitration_id == PID_REPLY and message.data[2] == ENGINE_RPM:
            # Convert data to RPM
            self.rpm = round(((message.data[3]*256) + message.data[4])/4)

    def _get_speed(self):
        GPIO.output(led,True)
        # Sent a Vehicle speed  request
        msg = can.Message(arbitration_id=PID_REQUEST,
                data=[0x02,0x01,VEHICLE_SPEED,0x00,0x00,0x00,0x00,0x00],
                extended_id=False)
        self.bus.send(msg)
        GPIO.output(led,False)

        # listen for response
        message = self.bus.recv()
        if message.arbitration_id == PID_REPLY and message.data[2] == VEHICLE_SPEED:
            # Convert data to km
            self.speed = message.data[3]

    def _get_throttle(self):
        GPIO.output(led,True)
        # Sent a Throttle position request
        msg = can.Message(arbitration_id=PID_REQUEST,
                data=[0x02,0x01,THROTTLE,0x00,0x00,0x00,0x00,0x00],
                extended_id=False)
        self.bus.send(msg)
        GPIO.output(led,False)

        message = self.bus.recv()
        if message.arbitration_id == PID_REPLY and message.data[2] == THROTTLE:
            # Conver data to throttle %
            self.throttle = round((message.data[3]*100)/255)


    def _update_fake_stats(self):
        self.speed = random.randint(0, 100)
        self.throttle = random.randint(0, 100)
        self.rpm= random.randint(0, 4500)
        self.coolant_temp = random.randint(0, 250)


    def shutdown(self):
        print("Shutting Down GPS Reader")
        self.exit.set()






