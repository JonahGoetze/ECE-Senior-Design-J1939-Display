from multiprocessing import Process, Event
import queue as Q
import time
import random
import csv

try:
    import adafruit_gps
except:
    print("adafruit_gps library not installed. Continuing.")

try:
    import board
except:
    print("board library not installed. Continuing.")

try:
    import busio
except:
    print("busiolibrary not installed. Continuing.")

try:
    import serial
except:
    print("serial not installed. Continuing.")

class GpsReader(Process):

    def __init__(self, queue, log_file_path, test=False):
        super(Process, self).__init__()
        self.queue = queue
        self.test = test
        self.exit = Event()

        self.speed = -1

        self.log_file_path = log_file_path

        if not test:
            self._setup_gps()
        self.last_timestamp = time.monotonic()

    def _setup_gps(self):

        uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3000)

        # Create a GPS module instance.
        self.gps = adafruit_gps.GPS(uart, debug=False)
        self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        self.gps.send_command(b'PMTK220,500')


    def run(self):
        print("Running GPS Reader")

        with open(self.log_file_path, "w") as log_file:
            self.csv_writer = csv.writer(log_file)
            self.csv_writer.writerow(["Speed"]) #write header

            while not self.exit.is_set():
                if not self.test:
                    self._update_speed()
                else:
                    self._update_fake_speed()

                if self.speed >= 0: #speed has been set
                    self._log_speed()


    def _log_speed(self):
        self.csv_writer.writerow([self.speed])

        try:
            self.queue.put(self.speed, True, 0.1)
        except Q.Full:
            pass #Don't let a full queue cause an issue


    def _update_speed(self):
       # Make sure to call gps.update() every loop iteration and at least twice
       # as fast as data comes from the GPS unit (usually every second).
       # This returns a bool that's true if it parsed new data (you can ignore it
       # though if you don't care and instead look at the has_fix property).
        self.gps.update()
        current = time.monotonic()
        if current - self.last_timestamp >= 1.0:
            self.last_timestamp = current
            if not self.gps.has_fix:
                # Try again if we don't have a fix yet
                print('Waiting for fix...')
                self.speed = -1
                return

            # We have a fix! (gps.has_fix is true)
            if self.gps.track_angle_deg is not None:
                    #convert knots to mph
                    self.speed = self.gps.speed_knots*1.15078

    def _update_fake_speed(self):
        current = time.monotonic()
        if current - self.last_timestamp >= 0.1:
            self.last_timestamp = current
            self.speed = random.randint(0, 50)

    def shutdown(self):
        print("Shutting Down GPS Reader")
        self.exit.set()





