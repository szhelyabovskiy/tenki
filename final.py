import smbus
import time
import math
from pressure import getPressure, init_Pressure
from direction import getDirection, getDeclination
from send import sendMQTT

#The code is split into several functions, to avoid clutter.
#Module pressure.py deals with the pressure & temperature module.
#Module direction.py deals with the compass module.
#Module send.py deals with MQTT.

#Processor time management is not required for this project. This is due to the fact that,
#well, weather can't change over a span of several seconds. Hence, fast data collection is 
#not needed.

#The dict below holds the data to be sent over MQTT.
data = {'direction': 180, 
	'temperature': 20,
	'pressure': 103}

#This constant controls frequency of readings
dataInterval = 10;

#Initialisation sequences for the modules
declination = getDeclination() 		#magnetic
calibrationData = init_Pressure()	#pressure
print(declination)

#Infinite loop to collect and send data
while(True):
	time.sleep(dataInterval)

	#Fill the dict with fresh measurements
	data['direction'] = getDirection(declination)
	pres_data = getPressure(calibrationData)
	data['temperature'] = pres_data['temp']
	data['pressure'] = pres_data['pres']

	#Send data over
	sendMQTT(data)
