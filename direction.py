import smbus
import time
import math
import RPi.GPIO as GPIO 
from time import sleep 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)

#This module receives and converts data from the HMC5883L magnetic sensor that reads off the #direction of the weather vane.
#Principle of operation:
#A magnet attached to the vane overpowers Earth's magnetic field next to the sensor. Using the #direction of this magnetic field, wind direction can be determined.

#1) 	At plug in, getDeclination() is called.
#	The user has about 20 seconds to turn the arrow towards true north.
#	This is indicated by a flashing LED with accelerating flash frequency.
#2)	After that, getDirection() calculates the direction of the vane relative to the original
#	declination. The LED stays on, to show that the device is calibrated.

time.sleep(6)

bus = smbus.SMBus(1)

addrR = 0x1E
pi = 3.14159265359
output = 0

def getDeclination():
	#This function returns the initial orientation of the device, later used as reference.
	bus.write_byte_data(addrR, 0x00, 0x70)
	bus.write_byte_data(addrR, 0x01, 0xA0)
	bus.write_byte_data(addrR, 0x02, 0x00)

	#Flashing of the LED indicates that calibration is in progress.
	#Accelerated flashing indicates that time is running out.
	i = 0;
	while (i < 5):
		time.sleep(1)
		GPIO.output(11, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(11, GPIO.LOW)
		i = i + 1
	while (i < 11):
		time.sleep(0.5)
		GPIO.output(11, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(11, GPIO.LOW)
		i = i + 1
	GPIO.output(11, GPIO.HIGH)
	return getDirection(0)

def getVal(adr):
	#This function reads and merges two bytes into a single value.
	msb = bus.read_byte_data(addrR, adr)
	lsb = bus.read_byte_data(addrR, adr + 1)
	return (msb << 8)+lsb

def getDirection(declination):
	#This function collects and returns vane orientation data in degrees from 0 to 360.
	
	#Raw data is stored in a list. Only x and y axes are used.
	output = [0,0,0]
	output[0] = getVal(3) #x
	output[1] = getVal(7) #z
	output[2] = getVal(5) #y
	
	#The module's raw coordinates are not perfect. Using experimentation, these 
	#compensation values have been found to correct this offset.
	coef = [180, 280, 0]

	#Sign and offset correction
	for j in range (3):
		if (output[j] > 32768):
			output[j] = output[j] - 65536
		output[j] = output[j] + coef[j]
	
	#Find the angle from the two coordinates using arctan
	heading = math.atan2(output[1], output[0])
	if (heading < 0):
		heading  = heading + 2*pi

	#Compare the resultant angle to the reference
	heading_angle = int(heading*180/pi) - declination
	if (heading_angle < 0):
		heading_angle = heading_angle + 360
	return heading_angle
