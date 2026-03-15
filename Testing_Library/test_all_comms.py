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
pinOut = DigitalOutput("2")
pinIn = DigitalInput("11")
pinReset = DigitalOutput("3")

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
	value = round(random.uniform(0.0, 1.0), 2) # Generate random 2 d.p. float
	
	pinOut.write(value)
	print(f'READING IN PIN VALUE: {pinOut.read()}')

if __name__ == "__main__":
	pinReset.on()
	pinOut.off()
	input("PRESS ENTER TO CONTINUE")
	# Wait for nucleo
	while pinIn.read() == 1:
		pinOut.off()
		time.sleep(0.1)

	print("SENDING CAN MESSAGE")
	# CAN Testing
	pinOut.on() # Signal Nucleo
	canBus = CANBus()
	testWrite(canBus)

	pinOut.off() # Block nucleo from proceeding
	
	print("WAITING FOR CAN MESSAGE")
	# Check that nucleo modified pin to 1 to switch to receiving
	while pinIn.read() == 0:
		pinOut.off()
		#print(pinIn.read())
		time.sleep(0.1)
		
	print("READING CAN MESSAGE")
	testReadThread(canBus)

	print("SENDING ANALOG MESSAGE")
	pinAnalogOut = AnalogOutput("6")
	test_analog_class(pinAnalogOut)
	pinOut.on()
	time.sleep(0.1)
	pinOut.off() # Reset to run again
