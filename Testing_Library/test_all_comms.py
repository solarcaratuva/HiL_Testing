import sys
sys.path.append('/home/solarcar/solarcar/HiL_Testing/Server')

from CANBus import CANBus
from CANMessage import CanMessage
from CANPi import readIn
import time
import serial
from gpioPins import DigitalInput, DigitalOutput
import random
import gpiozero
from gpioPins import AnalogOutput

# Global Pins for Synchronization
pinOut = DigitalOutput("GPIO2")
pinIn = DigitalInput("GPIO11")

# -----------Testing CAN Comms-----------

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
	time.sleep(1) # Wait for Nucleo to send CAN
	counter = 0
	while (counter < 5):
		print(f'Reading number {counter}')
		canBus.printCANBus()
		time.sleep(0.5)
		counter = counter + 1
		
#Send BPSError to Nucleo (currently turn LD2 off and on)
def testWrite(canBus : CANBus):
	#Example CANMessage
	name = "BPSError"
	id = 0x106
	signals = {"internal_communications_fault" : 1}
	timestamp = 1.0
	can_message = CanMessage(name, id, signals, timestamp)
	counter = 0
	canBus.sendMessage(can_message)
		
def testCAN():
	canBus = CANBus()
	testWrite(canBus)

	pinOut.value = 0 # Block nucleo from proceeding
	# Check that nucleo modified pin to 1 to switch to receiving
	while pinIn.value == 0:
		pinOut.value = 0
		time.sleep(0.1)

	testReadThread(canBus)

#----------------Testing Analog Comms---------------

#Test case without the wrapper api
def send_to_nucleo():	
	pinOut = gpiozero.PWMOutputDevice("GPIO5", frequency=5000)

	#Sending analog value to nucleo
	while True:
		pinOut.value = 0.64
		print(f"SENDING {pinOut.value}")
		#pinOut.pulse() #Useful function to sweep all ranges

		time.sleep(2)

#Test the wrapper api
def test_analog_class(pinOut):
	value = round(random.uniform(1.0, 100.0), 2) # Generate random 2 d.p. float
	
	pinOut.write_voltage(value)
	print(f'READING IN PIN VALUE: {pinOut.read()}')

def testAnalog():
	pinOut = AnalogOutput("5")
	test_analog_class(pinOut)

if __name__ == "__main__":
	# Wait for nucleo
    while pinIn.value == 1:
		pinOut.value = 0
		time.sleep(0.1)

	pinOut.value = 1
	testCAN()

	# Make sure finished sending
	while pinIn.value == 1:
		pinOut.value = 0
		print("THERE WAS A SYNC ERROR WITH RECEIVING CAN")
		time.sleep(0.1)

	pinOut.value = 1
	testAnalog()