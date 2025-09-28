from gpioPins import *
import time

pinOut = AnalogOutput("GPIO11")

while True:
    # turn on
    print("turning on")
    pinOut.on()
    time.sleep(2)
    # turn off 
    print("turning off")
    pinOut.off()
    time.sleep(2)

    # write a value of 0.5 to the AnalogOutput pin and rad
    pinOut.write(0.5)
	print(pinOut.read())
    time.sleep(2)