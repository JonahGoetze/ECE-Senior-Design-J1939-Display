from hat_adapter_abc import HatAdapter
from queue_manager import QueueManager
from queue import Empty
import os
import time
import adafruit_gps
import serial
import RPi.GPIO as GPIO
import logging
import j1939
import can
from enum import IntEnum

class PGN (IntEnum):
    EEC1 = 61444
    ET1 = 65262
    VEP1 = 65271

class PID (IntEnum):
    EMS01 = 768
    EMS12 = 779

class HatManager(HatAdapter):
    def __init__(self, queue_manager):
        super().__init__(queue_manager)
        self.log_level = logging.INFO # change to INFO for normal use, DEBUG for testing purposes
        self.log = logging.getLogger("hat_manager")
        self.log.setLevel(self.log_level)
        sh = logging.StreamHandler()
        sh.setLevel(self.log_level)
        self.log.addHandler(sh)
        self.PGN_whitelist = [] #[PGN.EEC1, PGN.ET1, PGN.VEP1] #PGN filter
        self.PID_whitelist = [PID.EMS01, PID.EMS12]
        self.led_state = False

    def loop(self):
        # check to see if we have a new can message
        try:
            message = self.can_listener.buffer.get(block=False)
        except Empty:
            message = None

        if message is not None:
            self.led_state = not self.led_state
            GPIO.output(self.led, self.led_state)

            self.on_raw_can_message(message)
        self.update_gps()

    def startup_hook(self):

        logging.getLogger('j1939').setLevel(self.log_level)
        logging.getLogger('can').setLevel(self.log_level)

        self.log.info("Initializing")
        os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")

        self.led = 22
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.led,GPIO.OUT)
        GPIO.output(self.led,True)

        # create the ElectronicControlUnit (one ECU can hold multiple ControllerApplications)
        self.ecu = j1939.ElectronicControlUnit()
    
        # Connect to the CAN bus
        self.ecu.connect(bustype='socketcan', channel='can0')

        # subscribe to all (global) messages on the bus
        self.ecu.subscribe(self.on_j1939_message)

        # can interface setup
        self.can_bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
        can_filters = [{"can_id": i, "can_mask": 0xF, "extended": False} for i in self.PID_whitelist]
        self.can_bus.set_filters(can_filters)
        self.can_listener = can.BufferedReader()
        self.can_notifier = can.Notifier(self.can_bus, [self.can_listener])
        
        # gps setup
        uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3000)

        # Create a GPS module instance.
        self.gps = adafruit_gps.GPS(uart, debug=False)
        self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        self.gps.send_command(b'PMTK220,500')
        self.gps_last_timestamp = time.monotonic()
        self.gps_speed = -1

    def shutdown_hook(self):
        self.log.info("Deinitializing")
        self.ecu.disconnect()
        GPIO.output(self.led,False)
        os.system("sudo /sbin/ip link set can0 down")

        self.can_notifier.stop()
        self.can_bus.shutdown()

    def on_raw_can_message(self, message):
        if message.arbitration_id == PID.EMS01:
            word = message.data[0:2]
            engspd = int.from_bytes(word,byteorder="big",signed = False) # convert bytearray to int
            engspd = round(engspd) 
            self.queue_manager.rpm.put(engspd)
        elif message.arbitration_id == PID.EMS12:
            coolnttemp = message.data[0]
            coolnttemp = (coolnttemp*0.625)-10
            coolnttemp = (coolnttemp*(9/5))+32
            coolnttemp = round(coolnttemp,2)
            self.queue_manager.temp.put(coolnttemp)
            pass
        else:
            pass

            

    def on_j1939_message(self, priority, pgn, sa, timestamp, data):
        """Receive incoming messages from the bus

        :param int priority:
            Priority of the message
        :param int pgn:
            Parameter Group Number of the message
        :param int sa:
            Source Address of the message
        :param int timestamp:
            Timestamp of the message
        :param bytearray data:
            Data of the PDU
        """
        if pgn not in self.PGN_whitelist:
            #self.log.debug(f"PGN ignored: {pgn}")
            return
        elif pgn == PGN.EEC1:
            word = data[3:5]
            engspd = int.from_bytes(word,byteorder="little",signed = False) # convert bytearray to int
            engspd *= 0.125 # engspeed resolution
            engspd = round(engspd) 
            self.queue_manager.rpm.put(engspd)
        elif pgn == PGN.ET1:
            coolnttemp = data[0]
            coolnttemp = (coolnttemp*(9/5))+32
            coolnttemp = round(coolnttemp,1)
            self.queue_manager.temp.put(coolnttemp)
        elif pgn == PGN.VEP1:
            word = data[4:6]
            voltage = int.from_bytes(word,byteorder="little",signed = False)
            voltage *= 0.05 # Voltage resolution
            voltage = round(voltage,2) 
            self.queue_manager.voltage.put(voltage)
        else:
            pass
        #self.log.debug(f"PGN {pgn} length {len(data)} Data {data.hex()}")


    def update_gps(self):
        # Make sure to call gps.update() every loop iteration and at least twice
        # as fast as data comes from the GPS unit (usually every second).
        # This returns a bool that's true if it parsed new data (you can ignore it
        # though if you don't care and instead look at the has_fix property).
        self.gps.update()
        current = time.monotonic()
        if current - self.gps_last_timestamp >= 1.0:
            self.gps_last_timestamp = current
            if not self.gps.has_fix:
                # Try again if we don't have a fix yet
                self.log.debug('Waiting for fix...')
                self.gps_speed = -1

            # We have a fix! (gps.has_fix is true)
            elif self.gps.track_angle_deg is not None:
                    #convert knots to mph
                    self.gps_speed = self.gps.speed_knots*1.15078
        if self.gps_speed>-1:
            self.queue_manager.gps_speed.put(self.gps_speed)
        else:
            self.queue_manager.gps_speed.put(-1)