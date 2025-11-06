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

def testGPIOInAndOut():
	#Test GPIO2 (output) and GPIO11 (input)
	#Turn GPIO2 on (default state) and GPIO11 should turn on from the nucleo; can also use wait_for_active
	
	#turn on GPIO2
	pinOut = gpiozero.DigitalOutputDevice("GPIO2");
	pinIn = gpiozero.DigitalInputDevice("GPIO11");

	pinOut.on()
	while True:
		print(f'THIS IS THE PIN IN VALUE (GPIO 11): {pinIn.value}')
		print(f'THIS IS THE PIN OUT VALUE (GPIO 2): {pinOut.value}')
		#pinIn.wait_for_active()
		#print("IT IS ACTIVE")
		time.sleep(3)
