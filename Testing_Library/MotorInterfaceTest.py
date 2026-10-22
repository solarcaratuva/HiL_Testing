import sys
import serial
import time
import threading

sys.path.append('/home/solarcar/solarcar/HiL_Testing/Server')

THROTTLE_ADDR = 0x2F
REGEN_ADDR = 0x2E
THROTTLE_START_BYTE = b'\xFF'
REGEN_START_BYTE = b'\xFE'

class MotorInterfaceTest:
    """One Pico session. Latest throttle (0x2F) and regen (0x2E), no mode switch."""
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        self.stop_thread = False
        self.mru_throttle = None # Most Recently Used Throttle Value
        self.mru_regen = None    # Most Recently Used Regen Value
        self.Lock = threading.Lock()
        self._marker = None
        self._buf = bytearray()
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )
        print("Waiting for Pico to start...")
        time.sleep(2)  # Give the Pico time to boot
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
                    if byte_read:
                        self.feed(byte_read)
                except serial.SerialException as e:
                    print(e)
                    # setting Both to None so that Exception is triggered within the getter methods
                    self.mru_throttle = None
                    self.mru_regen = None

    def feed(self, data):
        for byte in data:
            self._feed_byte(byte)

    def _feed_byte(self, byte):
        if self._marker is None:
            if byte == THROTTLE_START_BYTE[0] or byte == REGEN_START_BYTE[0]:
                self._marker = byte
                self._buf.clear()
            return
        self._buf.append(byte)
        if len(self._buf) < 2:
            return
        # MotorBoard sends (0x100 - value). Low 8 bits, then bit 8.
        raw = self._buf[0] | ((self._buf[1] & 0x01) << 8)
        value = 256 - raw
        with self.Lock:
            if self._marker == THROTTLE_START_BYTE[0]:
                self.mru_throttle = value
            else:
                self.mru_regen = value
        self._marker = None
        self._buf.clear()

    def read(self):
        """Latest throttle and regen counts from this session. None until seen."""
        with self.Lock:
            return self.mru_throttle, self.mru_regen

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


def _frame(marker, received):
    """Bytes the Pico writes for one I2C write. `received` is the 9-bit word on the bus."""
    if received > 256:
        received = 256
    return bytes((marker, received & 0xFF, (received >> 8) & 0x01))


def _demo():
    assert THROTTLE_ADDR == 0x2F and REGEN_ADDR == 0x2E
    session = MotorInterfaceTest.__new__(MotorInterfaceTest)
    session.mru_throttle = None
    session.mru_regen = None
    session.Lock = threading.Lock()
    session._marker = None
    session._buf = bytearray()
    # MotorBoard writes 0x100 - value. Both land in one read; the second
    # throttle write must leave regen alone.
    session.feed(_frame(0xFF, 0x100 - 100) + _frame(0xFE, 0x100 - 40))
    assert session.read() == (100, 40)
    session.feed(_frame(0xFF, 0x100 - 0))
    assert session.read() == (0, 40)
    assert session.get_throttle() == 0.0
    assert session.get_regen_raw() == 40


if __name__ == "__main__":
    _demo()
