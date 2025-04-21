import sys
sys.path.append('/home/solarcar/solarcar/HiL_Testing/Server')

from CANBus import CANBus
from CANMessage import CanMessage
from CANPi import readIn
import time
import serial
from gpioPins import DigitalInput, DigitalOutput


def testAddMethod(canBus : CANBus):
	canBus.printCANBus()

	input("WAITING")
	#Example CANMessage
	name = "BPSError"
	id = 0x106
	signals = {"internal_communications_fault" : 1}
	timestamp = 1.0
	can_message = CanMessage(name, id, signals, timestamp)
	canBus.addToCANBus(can_message)
	canBus.printCANBus()

def testReadThread(canBus : CANBus):
	counter = 0
	while (counter < 10):
		print(f'Reading number {counter}')
		canBus.printCANBus()
		time.sleep(0.5)
		counter = counter + 1
		
def testWrite(canBus : CANBus):
	#Example CANMessage
	name = "BPSError"
	id = 0x106
	signals = {"internal_communications_fault" : 1}
	timestamp = 1.0
	can_message = CanMessage(name, id, signals, timestamp)
	counter = 0
	while (counter < 5):
		print(f'Sending number {counter}')
		canBus.sendMessage(can_message)
		time.sleep(2)
		counter = counter + 1

canBus = CANBus()

