import gipozero

"""
DigitalOutput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Write (validate input based on established range)
        

DigitalInput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Read : bool
"""

class DigitalInput:
    #Validate the Pin Number
    def __PinValidate(self, pinName):
        #Less than 27
        return 2 <= int(pinName) < 27

    #Constructor
    def __init__(self, init_pinName: str):
        if (__PinValidate(init_pinName)):
            self.pinName = init_pinName

