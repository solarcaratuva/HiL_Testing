#IMPORTANT NOTES:
#Constructors use default values from gpiozero
#DigitalOutput: Active High, Intitial Value-0, 
#DigitalInput: Pulldown resistor, Active High, No bounce compensation
import gpiozero
import json
import os

#IMPORTANT NOTES:
#Constructors use default values from gpiozero
#DigitalOutput: Active High, Intitial Value-0, 
#DigitalInput: Pulldown resistor, Active High, No bounce compensation

"""
DigitalOutput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Write (validate input based on established range)
        On (turn pin on)
        Off (turn pin off)
        Toggle (toggle state of pin)
"""
class DigitalOutput:

    #Validate the Pin Number
    #INPUT: self and pinName as a string
    #OUTPUT: returns the pin_number from mapping
    def __PinValidate(self, pinName):
        #pin mapping json
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        # Load pin mappings from the config file
        with open(config_file, 'r') as f:
            pin_map = json.load(f)
        
        # Map the pin name to an integer GPIO pin number
        if pinName in pin_map:
            pin_number = pin_map[pinName]
        else:
            raise ValueError(f"Pin name '{pinName}' not found in config file.")
        
        return pin_number

    #Constructor
    #INPUT: self, pinName as a string
    #OUTPUT: pin object that represents 
    def __init__(self, pinName: str):
        self.pinName = pinName
        self.pinNumber = self.__PinValidate(pinName=pinName)
        self.pinObject = gpiozero.DigitalOutputDevice(self.pinNumber)

    #Writes to the digital pin
    def write(self, state: bool) -> None:
        if not isinstance(state, bool):
            raise TypeError("Argument must be of type BOOL")

        if state: 
            self.pinObject.on()
        else:
            self.pinObject.off() 
    
    def on(self) -> None:
        self.pinObject.on()

    def off(self) -> None:
        self.pinObject.off()

    def toggle(self) -> None:
        self.pinObject.toggle()

    #returns the current state of the pin
    def read(self) -> bool:
        return self.pinObject.value
        
""""
DigitalInput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Read : bool
"""

class DigitalInput:
    #Validate the Pin Number
    #INPUT: self and pinName as a string
    #OUTPUT: returns the pin_number from mapping
    def __PinValidate(self, pinName: str) -> bool:
        #pin mapping json
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        # Load pin mappings from the config file
        with open(config_file, 'r') as f:
            pin_map = json.load(f)
        
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
        self.pinObject = gpiozero.DigitalInputDevice(self.pinNumber)

    #Read function: returns a boolean 
    def read(self) -> bool:
        return self.pinObject.is_active

