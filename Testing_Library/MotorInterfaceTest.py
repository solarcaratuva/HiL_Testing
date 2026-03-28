import sys
import serial
import time
import threading

sys.path.append('/home/solarcar/solarcar/HiL_Testing/Server')

THROTTLE_ADDR = 0x2F
REGEN_ADDR = 0x2E
THROTTLE_START_BYTE = b'\xFF'
REGEN_START_BYTE = b'\xFE'
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

class MotorInterfaceTest:
    """API for test Motor interface"""
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        self.stop_thread = False
        self.mru_throttle = None # Most Recently Used Throttle Value
        self.mru_regen = None    # Most Recently Used Regen Value
        self.Lock = threading.Lock()
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )
        print("Waiting for Arduino to start...")
        time.sleep(2)  # Give Arduino time to boot
        self.startReadThread()


    # Run infinite thread to read in Throttle and Regen Values
    def startReadThread(self):
        read_thread = threading.Thread(target=self.readThrottleAndRegen)
        read_thread.daemon = True
        try: 
            read_thread.start()
        except RuntimeError as e:
            raise RuntimeError("Thread Was not Started")
    
    # Constantly read thorttle and regen values
    def readThrottleAndRegen(self):
        while(not self.stop_thread):
                try: 
                    byte_read = self.ser.read(1)

                    if byte_read == THROTTLE_START_BYTE:  # Throttle start marker
                        data = self.ser.read(2)  # Read 2 bytes for 9-bit value
                        if len(data) == 2:
                            # motorinterface.cpp sends (0x100 - throttle) 
                            # first byte contains lower 8 bits, second byte LSB is the 9th bit
                            raw_from_arduino = data[0] | ((data[1] & 0x01) << 8)
                            with self.Lock:
                                self.mru_throttle = 256 - raw_from_arduino  # PowerBoard sends (0x100 - throttle) over I2C
                        
                    elif byte_read == REGEN_START_BYTE: 
                        data = self.ser.read(2)  # Read 2 bytes for 9-bit value
                        if len(data) == 2:
                            # motorinterface.cpp sends (0x100 - regen)
                            # first byte contains lower 8 bits, second byte LSB is the 9th bit
                            raw_from_arduino = data[0] | ((data[1] & 0x01) << 8)
                            with self.Lock:
                                self.mru_regen = 256 - raw_from_arduino  # PowerBoard sends (0x100 - regen) over I2C

                except serial.SerialException as e:
                    print(e)
                    # setting Both to None so that Exception is triggered within the getter methods
                    self.mru_throttle = None
                    self.mru_regen = None
                                
    def get_throttle(self) -> float:
        # Normalized between [0-1.0]
        with self.Lock:
            if self.mru_throttle is None:
                raise ValueError('MRU-Throttle Value is None')
            return self.mru_throttle / 256.0
        
    def get_throttle_raw(self) -> int:
        # raw between [0-256]
        with self.Lock:
            if self.mru_throttle is None:
                raise ValueError('MRU-Raw-Throttle Value is None')
            return self.mru_throttle
    
    def get_regen(self) -> float:
        # Normalized between [0,1.0]
        with self.Lock:
            if self.mru_regen is None:
                raise ValueError('MRU-Regen Value is None')
            return self.mru_regen / 256.0
        
    def get_regen_raw(self) -> int:
        # raw between [0-256]
        with self.Lock:
            if self.mru_regen is None:
                raise ValueError('MRU-Regen-Raw Value is None')
            return self.mru_regen

    def close(self):
        self.stop_thread = True
        if self.ser and self.ser.is_open:
            self.ser.close()

