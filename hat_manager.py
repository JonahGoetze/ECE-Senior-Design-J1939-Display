from hat_adapter_abc import HatAdapter
from queue_manager import QueueManager
import os
import RPi.GPIO as GPIO
import logging
import j1939


class HatManager(HatAdapter):
    def __init__(self, queue_manager):
        super().__init__(queue_manager)
        self.log = logging.getLogger("hat_manager")
        self.log.setLevel(logging.DEBUG)

    def loop(self):
        pass

    def startup_hook(self):

        logging.getLogger('j1939').setLevel(logging.DEBUG)
        logging.getLogger('can').setLevel(logging.DEBUG)

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
        data.hex()
        self.log.debug("PGN {} length {} Data {}".format(pgn, len(data), data.hex()))
