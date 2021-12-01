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
import serial


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
