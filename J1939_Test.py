import RPi.GPIO as GPIO
import logging
import time
import can
import j1939
import os

led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)

logging.getLogger('j1939').setLevel(logging.DEBUG)
logging.getLogger('can').setLevel(logging.DEBUG)

def on_message(priority, pgn, sa, timestamp, data):
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
    print("PGN {} length {} Data {}".format(pgn, len(data), data.hex()))

def main():
    print("Initializing")
    os.system("sudo /sbin/ip link set can0 up type can bitrate 250000")

    # create the ElectronicControlUnit (one ECU can hold multiple ControllerApplications)
    ecu = j1939.ElectronicControlUnit()
    
    # Connect to the CAN bus
    ecu.connect(bustype='socketcan', channel='can0')

    # subscribe to all (global) messages on the bus
    ecu.subscribe(on_message)
    time.sleep(120)

    print("Deinitializing")
    ecu.disconnect()
    GPIO.output(led,False)
    os.system("sudo /sbin/ip link set can0 down")

if __name__ == '__main__':
    main()

#except KeyboardInterrupt:
	#os.system("sudo /sbin/ip link set can0 down")
