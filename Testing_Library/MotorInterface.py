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