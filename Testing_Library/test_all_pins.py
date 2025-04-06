import gpiozero
import time
import os

def turnAllOff():
	for i in range(2,28):
		pinOut = gpiozero.DigitalOutputDevice("GPIO" + str(i))
		pinOut.off()
		input("WAITING TO TURN OFF: " + str(i+1))
		
def turnAllOn():
	for i in range(2,28):
		pinOut = gpiozero.DigitalOutputDevice("GPIO" + str(i))
		pinOut.on()
		input("WAITING TO TURN ON: " + str(i+1))
	
turnAllOn()
turnAllOff()
time.sleep(3)
print("Ending")
