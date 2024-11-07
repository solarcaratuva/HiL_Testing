import gipozero
import json

"""
DigitalOutput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Write (validate input based on established range)

"""
class DigitalOutput:

    #Constructor
    def __init__(self, pinName: str):
        self.pinName = pinName



        
""""
DigitalInput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Read : bool
"""
