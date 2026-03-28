import sys
sys.path.append("/home/solarcar/solarcar/HiL_Testing/Server")

import gpiozero
import time


print("[RESET] Resetting Nucleo via GPIO3...")

# intiialize reset pin as output (active low)
reset_pin = gpiozero.DigitalOutputDevice("GPIO3")

try:
	# hold reset low
	reset_pin.off()
	time.sleep(0.1)  # 100 ms pulse

	# release reset (set high)
	reset_pin.on()

	print("[RESET] Nucleo reset complete.")
finally:
	pass
