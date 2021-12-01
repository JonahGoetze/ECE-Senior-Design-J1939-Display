#!/usr/bin/python3
#
## obdii_logger.py
# 
# This python3 program sends out OBDII request then logs the reply to the sd card.
# Make sure Python-CAN is installed first http://skpang.co.uk/blog/archives/1220
#
#

import RPi.GPIO as GPIO
import can
import time
import os
import queue
import csv
from datetime import datetime
from threading import Thread
import board
import busio
import adafruit_gps
import serial

#uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3000)

#! Create a GPS module instance.
#speed=0
#gps = adafruit_gps.GPS(uart, debug=False)
#gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
#gps.send_command(b'PMTK220,500')
#last_print = time.monotonic()
#while True:
    #! Make sure to call gps.update() every loop iteration and at least twice
    #! as fast as data comes from the GPS unit (usually every second).
    #! This returns a bool that's true if it parsed new data (you can ignore it
    #! though if you don't care and instead look at the has_fix property).
    #gps.update()
    #current = time.monotonic()
    #if current - last_print >= 1.0:
        #last_print = current
        #if not gps.has_fix:
            #! Try again if we don't have a fix yet
	    #print('Waiting for fix...')
            #continue
        # We have a fix! (gps.has_fix is true)
    #if gps.track_angle_deg is not None:
            #speed=(('{}'.format(gps.speed_knots))*1.15078) #!convert knots to mph
	
led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)

# For a list of PIDs visit https://en.wikipedia.org/wiki/OBD-II_PIDs
ENGINE_COOLANT_TEMP = 0x05
ENGINE_RPM          = 0x0C
VEHICLE_SPEED       = 0x0D
MAF_SENSOR          = 0x10
O2_VOLTAGE          = 0x14
THROTTLE            = 0x11

PID_REQUEST         = 0x7DF
PID_REPLY           = 0x7E8

filename1 = datetime.now().strftime("%Y%m%d-%H%M%S")


print('\n\rCAN Rx test')
print('Bring up CAN0....')

# Bring up can0 interface at 500kbps
os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
time.sleep(0.1)	
print('Ready')

try:
	bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
except OSError:
	print('Cannot find PiCAN board.')
	GPIO.output(led,False)
	exit()

def can_rx_task():	# Receive thread
	while True:
		message = bus.recv()
		if message.arbitration_id == PID_REPLY:
			q.put(message)			# Put message into queue

def can_tx_task():	# Transmit thread
	while True:

		GPIO.output(led,True)
		# Sent a Engine coolant temperature request
		msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,ENGINE_COOLANT_TEMP,0x00,0x00,0x00,0x00,0x00],extended_id=False)
		bus.send(msg)
		time.sleep(0.05)

		# Sent a Engine RPM request
		msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,ENGINE_RPM,0x00,0x00,0x00,0x00,0x00],extended_id=False)
		bus.send(msg)
		time.sleep(0.05)

		# Sent a Vehicle speed  request
		msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,VEHICLE_SPEED,0x00,0x00,0x00,0x00,0x00],extended_id=False)
		bus.send(msg)
		time.sleep(0.05)		

		# Sent a Throttle position request
		msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,THROTTLE,0x00,0x00,0x00,0x00,0x00],extended_id=False)
		bus.send(msg)
		time.sleep(0.05)
		
		GPIO.output(led,False)
		time.sleep(0.1)
						
						
q = queue.Queue()
rx = Thread(target = can_rx_task)  
rx.start()
tx = Thread(target = can_tx_task)
tx.start()

temperature = 0
rpm = 0
speed = 0
throttle = 0
c = ''
count = 0

# Main loop
try:
	with open(filename1 +".csv", "w") as f:
		writer = csv.writer(f)
		writer.writerow(("Count","Coolant Temp","RPM","Speed","Throttle %"))
		while True:
			while(q.empty() == True):	# Wait until there is a message
				pass
			message = q.get()
			
			c = '{0:f},{1:d},'.format(message.timestamp,count)
			if message.arbitration_id == PID_REPLY and message.data[2] == ENGINE_COOLANT_TEMP:
				temperature = ((message.data[3] - 40)*(9/5))+32			#Convert data into temperature in degrees F

			if message.arbitration_id == PID_REPLY and message.data[2] == ENGINE_RPM:
				rpm = round(((message.data[3]*256) + message.data[4])/4)	# Convert data to RPM

			if message.arbitration_id == PID_REPLY and message.data[2] == VEHICLE_SPEED:
				speed = message.data[3]						# Convert data to km

			if message.arbitration_id == PID_REPLY and message.data[2] == THROTTLE:
				throttle = round((message.data[3]*100)/255)			# Conver data to throttle %

			c += '{0:3.2f},{1:4d},{2:3d},{3:3d}'.format(temperature,rpm,speed,throttle)
			print('\r {} '.format(c))
			writer.writerow((count,temperature, rpm, speed, throttle)) # Write data to file
			f.flush()
			count += 1
			

 
	
except KeyboardInterrupt:
	#Catch keyboard interrupt
	GPIO.output(led,False)
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	
