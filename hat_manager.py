from hat_adapter_abc import HatAdapter
from queue_manager import QueueManager
import os
import RPi.GPIO as GPIO
import logging
import j1939
from enum import IntEnum
from math import round

class PGN (IntEnum):
    EEC1 = 61444
    ET1 = 65262
    VEP1 = 65271

class HatManager(HatAdapter):
    def __init__(self, queue_manager):
        super().__init__(queue_manager)
        self.log_level = logging.DEBUG # change to INFO for normal use, DEBUG for testing purposes
        self.log = logging.getLogger("hat_manager")
        self.log.setLevel(self.log_level)
        sh = logging.StreamHandler()
        sh.setLevel(self.log_level)
        self.log.addHandler(sh)
        self.PGN_whitelist = [PGN.EEC1, PGN.ET1, PGN.VEP1] #PGN filter

    def loop(self):
        pass

    def startup_hook(self):

        logging.getLogger('j1939').setLevel(self.log_level)
        logging.getLogger('can').setLevel(self.log_level)

        self.log.info("Initializing")
        os.system("sudo /sbin/ip link set can0 up type can bitrate 250000")

        led = 22
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(led,GPIO.OUT)
        GPIO.output(led,True)

        # create the ElectronicControlUnit (one ECU can hold multiple ControllerApplications)
        self.ecu = j1939.ElectronicControlUnit()
    
        # Connect to the CAN bus
        self.ecu.connect(bustype='socketcan', channel='can0')

        # subscribe to all (global) messages on the bus
        self.ecu.subscribe(self.on_message)

    def shutdown_hook(self):
        self.log.info("Deinitializing")
        self.ecu.disconnect()
        GPIO.output(led,False)
        os.system("sudo /sbin/ip link set can0 down")

    def on_message(self, priority, pgn, sa, timestamp, data):
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
            self.log.debug(f"PGN ignored: {pgn}")
            return
        elif pgn == PGN.EEC1:
            word = data[3:5]
            engspd = int.from_bytes(word,byteorder="little",signed = False) # convert bytearray to int
            engspd *= 0.125 # engspeed resolution
            engspd = round(engspd) 
            self.queue_manager.rpm.put(engspd)
        elif pgn == PGN.ET1:
            pass
        elif pgn == PGN.VEP1:
            pass
        else:
            pass

        data.hex()
        self.log.debug("PGN {} length {} Data {}".format(pgn, len(data), data.hex()))
