import gpiozero
import time

pinOut = gpiozero.PWMOutputDevice("GPIO5", frequency=5000)

#Sending analog value to nucleo
while True:
	pinOut.value = 0.64
	print(f"SENDING {pinOut.value}")
    #pinOut.pulse() #Useful function to sweep all ranges

	time.sleep(2)
