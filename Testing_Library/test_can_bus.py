from CANBus import CANBus
from CANMessage import CanMessage
import time

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


canBus = CANBus()
#testAddMethod(canBus)

counter = 0
while (counter < 10):
	print(f'Reading number {counter}')
	canBus.printCANBus()
	time.sleep(2)
	counter = counter + 1


canBus.stopReadThread()
