import sys
import serial
import time

sys.path.append('/home/solarcar/solarcar/HiL_Testing/Server')

THROTTLE_ADDR = 0x2F
REGEN_ADDR = 0x2E

# Serial Configuration
ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=115200,  
    timeout=1
)

print("Waiting for Arduino to start...")
time.sleep(2)  # Give Arduino time to boot

while True:
    byte_read = ser.read(1)
    if byte_read == b'\xFF':   
        data = ser.read(3)  # Read 3 bytes for two 9-bit values
        if len(data) == 3:
            # Unpack two 9-bit values from 3 bytes
            # Byte 0: throttle[7:0]
            # Byte 1: throttle[8] in bit 0, regen[6:0] in bits 7:1
            # Byte 2: regen[8:7] in bits 1:0
            
            # Extracting throttle and regen
            throttle = data[0] | ((data[1] & 0x01) << 8) 
            regen = ((data[1] >> 1) & 0x7F) | ((data[2] & 0x03) << 7)  
            
            print(f"Throttle: {throttle}%) | Regen: {regen}}%)")
        else:
            print(f"Incomplete data: got {len(data)} bytes instead of 3")
    elif byte_read:
        print(f"Unexpected byte: {byte_read}")

'''
API for test Moto interface
'''
class Test_Motor_Interface:
    def __init__(self):
        self.mru_throttle = None
        self.mru_regen = None

    def get_throttle() -> float:
        # TODO Return throttle value as a double between [0-1]
        
        pass
    def get_throttle_raw() -> int:
        # TODO Return throttle value between [0-255]
        pass
    def get_regen() -> float:
        # TODO Return throttle value between [0-1]
        pass
    def get_regen_raw() -> int:
        # TODO Return throttle value between [0-255]
        pass


