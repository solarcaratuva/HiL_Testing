REG_SIZE = 4
IDR_OFFSET = 0x10
ODR_OFFSET = 0x14 # only 1st 2 bytes (of 4) are valid
BSRR_OFFSET = 0x18
LCKR_OFFSET = 0x1C

MEM_START = 0x48000000
MEM_PER_GROUP = 0x400

def readDigital(pinName: str) -> int:
    # ex. PA_7
    group = pinName[1]
    number = pinName[3]
    readAdr = MEM_START + (ord(group) - ord("A")) * MEM_PER_GROUP + ODR_OFFSET + number
    return readAdr

def writeDigital(pinName: str) -> int:
    pass

def readAnalog(pinName: str) -> int:
    pass

def writeAnalog(pinName: str) -> int:
    pass

# read a single bit in ODR for a specific digital pin's state
# values can be set using the BSRR register (?)
# analog states stored in the ADC registers (??)