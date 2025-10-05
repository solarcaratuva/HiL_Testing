import gpiozero
import time
from gpioPins import AnalogOutput


pinOut = AnalogOutput("5")

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
def test_analog_class():
	counter = 0.0
	print("TESTING VOLTAGE WRITE")
	while counter < 3.3:
		pinOut.write_voltage(counter)
		print(f'READING IN PIN VALUE: {pinOut.read()}')
		time.sleep(2)
		counter = counter + 0.3
	
	counter = 0.0
	print("TESTING PERCENTAGE WRITE")
	while counter < 1:
		pinOut.write(counter)
		print(f'READING IN PIN VALUE: {pinOut.read()}')
		time.sleep(2)
		counter = counter + 0.1
		

test_analog_class()
