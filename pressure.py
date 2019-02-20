import smbus
import time

bus = smbus.SMBus(1)
addrP = 0x77

def decode(input_bytes, sign):
	out = input_bytes[1] + (input_bytes[0] << 8)
	if (sign == 0 and out >= 32767):
		out = out - 65535
	return out

def init_Pressure():
	bus.write_byte_data(addrP, 0x02, 0x7000)
	time.sleep(2)
	calibrationData = {	'AC1':0,'AC2':0,'AC3':0,'AC4':0,'AC5':0,'AC6':0,
		   		'B1':0,'B2':0,'MB':0,'MC':0,'MD':0	}

	calibrationData['AC1'] = decode(bus.read_i2c_block_data(addrP, 0xAA, 2), 0)
	calibrationData['AC2'] = decode(bus.read_i2c_block_data(addrP, 0xAC, 2), 0)
	calibrationData['AC3'] = decode(bus.read_i2c_block_data(addrP, 0xAE, 2), 0)
	calibrationData['AC4'] = decode(bus.read_i2c_block_data(addrP, 0xB0, 2), 1)
	calibrationData['AC5'] = decode(bus.read_i2c_block_data(addrP, 0xB2, 2), 1)
	calibrationData['AC6'] = decode(bus.read_i2c_block_data(addrP, 0xB4, 2), 1)
	calibrationData['B1'] = decode(bus.read_i2c_block_data(addrP, 0xB6, 2), 0)
	calibrationData['B2'] = decode(bus.read_i2c_block_data(addrP, 0xB8, 2), 0)
	calibrationData['MB'] = decode(bus.read_i2c_block_data(addrP, 0xBA, 2), 0)
	calibrationData['MC'] = decode(bus.read_i2c_block_data(addrP, 0xBC, 2), 0)
	calibrationData['MD'] = decode(bus.read_i2c_block_data(addrP, 0xBE, 2), 0)
	return calibrationData

def readPTemp():
	bus.write_byte_data(addrP, 0xF4, 0x2E)
	time.sleep(0.005)
	return decode(bus.read_i2c_block_data(addrP, 0xF6, 2), 1)

def readPPres():
	bus.write_byte_data(addrP, 0xF4, 0x34)
	time.sleep(0.005)
	return decode(bus.read_i2c_block_data(addrP, 0xF6, 2), 1)

def getPressure(calibrationData):
	UT = readPTemp()
	X1 = ((UT - calibrationData['AC6']) * calibrationData['AC5']) / pow (2,15)
	X2 = (calibrationData['MC'] * pow (2,11)) / (X1 + calibrationData['MD'])
	B5 = X1 + X2
	result = {'temp': 0, 'pres': 0}
	result['temp'] = (B5 + 8)*0.1/pow (2, 4)
	UP = readPPres()
	B6 = B5 - 4000
	X1 = (calibrationData['B2'] * (B6 * B6/(pow (2, 12))))/pow (2, 11)	
	X2 = calibrationData['AC2'] * B6 / pow (2, 11)
	X3 = X1 + X2
	B3 = ((calibrationData['AC1'] * 4 + X3) + 2) / 4
	X1 = calibrationData['AC6'] * B6 / pow (2, 13)
	X2 = (calibrationData['B1'] * (B6 * B6/(pow (2, 12))))/pow (2, 16)
	X3 = ((X1 + X2) + 2) / 4
	B4 = calibrationData['AC4'] * (X3 + 32768) / pow(2, 15)
	B7 = (UP - B3) * 50000
	if (B7 < 0x80000000):
		p = (B7 * 2) / B4
	else:
		p = (B7/B4) * 2
	X1 = pow((p / pow(2, 8)), 2)
	X1 = (X1 * 3038) / pow(2, 16)
	x2 = (-7537 * p) / pow(2, 16)
	p = p + ((X1 + X2 + 3791)/pow(2, 4))
	result['pres'] = p * 0.01
	return result


