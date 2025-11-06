import sys
import serial
sys.path.append('/home/solarcar/solarcar/HiL_Testing/Server')

THROTTLE_ADDR = 0x2F
REGEN_ADDR  = 0x2E


'''
Both the throttle and regen are 9 it bit values, send them both at once in 
a 3 byte value and then just read based on there
'''
# TODO: Serial Configuration
ser = serial.Serial(
    port = '/dev/ttyAMA0',
    baudrate =115200, 
    timeout = 1
)


while True:
    if ser.read(1) == b'\xFF':   
        data = ser.read(2)
        if len(data) == 2:
            throttle_data = data[0]
            regen_data = data[1]
            print(f"Regen: {regen_data} Throttle: {throttle_data}")


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

