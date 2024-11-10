import gpiozero
import json

"""
DigitalOutput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Write (validate input based on established range)

"""
class DigitalOutput:

    #Validate the Pin Number
    #INPUT: self and pinName as a string
    #OUTPUT: Sets 
    def __PinValidate(self, pinName):
        #pin mapping json
        config_file = "config.json"
        # Load pin mappings from the config file
        try:
            with open(config_file, 'r') as f:
                pin_map = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file '{config_file}' not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Config file '{config_file}' contains invalid JSON.")
        
        # Map the pin name to an integer GPIO pin number
        if pinName in pin_map:
            pin_number = pin_map[pinName]
        else:
            raise ValueError(f"Pin name '{pinName}' not found in config file.")
        
        return pin_number

    #Constructor
    def __init__(self, pinName: str):
        self.pinName = pinName
        self.pinNumber = self.__PinValidate(pinName=pinName)
        self.pinObject = 




        
""""
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

