import paho.mqtt.client as mqtt
import json as js

#This module sends data over to the Mosquitto broker.

def sendMQTT(data):
	print("Sending!")

	#Convert dict to json string
	msg = js.dumps(data)
	print(msg)

	#Make a secure connection to Mosquitto
	client = mqtt.Client()
	client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt", keyfile="client.key")
	connected = False;
	while connected == False:
		try:
			client.connect("test.mosquitto.org", port=8884)
			connected = True
		except:
			print('Connection failed!')
			pass
	a = client.publish("IC.embedded/rs/data", msg)

	#For error debugging purposes:
	print(mqtt.error_string(a.rc))
