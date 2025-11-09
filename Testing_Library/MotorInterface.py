import pigpio
import time

# I2C Slave Addresses (one for throttle, one for regen)
THROTTLE_I2C_ADDRESS = 0x08 # placeholder values
REGEN_I2C_ADDRESS = 0x09

throttleCommands = []
regenCommands = []


# Helper classes
class ThrottleCommand:
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

class RegenCommand:
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp


# process received data
def process_i2c_data(address, data):
    value = (data[0] << 8) + data[1]
    timestamp = time.time()

    # store data in correct list
    if address == THROTTLE_I2C_ADDRESS:
        throttleCommands.append(ThrottleCommand(value, timestamp))
    elif address == REGEN_I2C_ADDRESS:
        regenCommands.append(RegenCommand(value, timestamp))
    

# Callback function for I2C
def i2c_callback(handle, address, data):
    process_i2c_data(address, data)


# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon")
    exit()

# Set up two I2C slave devices (one for throttle, one for regen)
throttle_handle = pi.i2c_open(1, THROTTLE_I2C_ADDRESS)
regen_handle = pi.i2c_open(1, REGEN_I2C_ADDRESS)

# Register callback functions
pi.i2c_slave_event(throttle_handle, lambda h, t, d: i2c_callback(h, THROTTLE_I2C_ADDRESS, d))
pi.i2c_slave_event(regen_handle, lambda h, t, d: i2c_callback(h, REGEN_I2C_ADDRESS, d))

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    pi.i2c_close(throttle_handle)
    pi.i2c_close(regen_handle)
    pi.stop()
import sys
import serial
import time
import threading


sys.path.append('/home/solarcar/solarcar/HiL_Testing/Server')

THROTTLE_ADDR = 0x2F
REGEN_ADDR = 0x2E

# Serial Configuration
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,  
    timeout=1
)

print("Waiting for Arduino to start...")
time.sleep(2)  # Give Arduino time to boot
'''
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
            
            print(f"Throttle: {throttle}%) | Regen: {regen})")
        else:
            print(f"Incomplete data: got {len(data)} bytes instead of 3")
    elif byte_read:
        print(f"Unexpected byte:{byte_read}")
'''
ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=9600,  
            timeout=1
        )
'''
API for test Motor interface
'''
class MotorInterface:
    def __init__(self):
        self.stop_thread = False
        self.mru_throttle = None
        self.mru_regen = None
        self.THROTTLE_ADDR = 0x2F
        self.REGEN_ADDR = 0x2E
        self.startReadThread()


    #Run infinite thread to read in Throttle and Regen Values
    def startReadThread(self):
        read_thread = threading.Thread(target=self.readThrottleAndRegen)
        read_thread.daemon = True
        try:
            read_thread.start()
        except ValueError as e:
            print(f"Exception")
    def readThrottleAndRegen(self):
        while(not self.stop_thread):
            with self.lock:
                byte_read = ser.read(1)
                if byte_read == b'\xFF':  # Start Byte
                    data = ser.read(3)  # Read 3 bytes for two 9-bit values
                    if len(data) == 3:
                        # two 9-bit values from 3 bytes
                        # Byte 0: throttle[7:0]
                        # Byte 1: throttle[8] in bit 0, regen[6:0] in bits 7:1
                        # Byte 2: regen[8:7] in bits 1:0

                        # Extracting throttle and regen
                        self.mru_throttle = data[0] | ((data[1] & 0x01) << 8) 
                        self.mru_regen = ((data[1] >> 1) & 0x7F) | ((data[2] & 0x03) << 7)  
                        
    def get_throttle(self) -> float:
        # Normalized between [0-1.0]
        if self.mru_throttle is None:
            return None
        return self.mru_throttle/256.0
    
    def get_throttle_raw(self) -> int:
        # raw between [0-256]
        if self.mru_throttle is None:
            return None
        return self.mru_throttle
    
    def get_regen(self) -> float:
        # Normalized between [0,1.0]
        if self.mru_regen is None:
            return None
        return self.mru_regen/256.0
    
    def get_regen_raw(self) -> int:
        # raw between [0-256]
        if self.mru_regen is None:
            return None
        return self.mru_regen


motor_interface = MotorInterface()

while(True):
    throttle_raw    = motor_interface.get_throttle_raw()
    throttle_norm   = motor_interface.get_throttle()
    regen_raw       = motor_interface.get_regen_raw() 
    regen_norm      = motor_interface.get_regen()







