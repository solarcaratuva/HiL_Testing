from gpio import *
import time

pinOut = DigitalOutput("GPIO2")
# pinIn = DigitalInput("GPIO3")
#When GPIO3 is set to digital input, a "GPIO3 has a physical pull-up resistor" error is thrown

pinIn = DigitalInput("GPIO11")

while True:
	pinOut.on()
	pinOut.on()
	pinOut.toggle()
	print("turning on")
	print(pinIn.read())
	time.sleep(3)
	print("turning off")
	pinOut.off()
	print(pinIn.read())
	time.sleep(3)
	print("turning on")
	pinOut.on()
	print(pinIn.read())
	time.sleep(3)
	print("turning off")
	pinOut.write(False)
	print(pinIn.read())
	time.sleep(3)

	
