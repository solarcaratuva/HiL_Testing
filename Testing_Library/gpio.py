#IMPORTANT NOTES:
#Constructors use default values from gpiozero
#DigitalOutput: Active High, Intitial Value-0, 
#DigitalInput: Pulldown resistor, Active High, No bounce compensation
import gpiozero
import json
import os

from Server.NucleoPinParser import parse_nucleo_pindef_pins, parse_gpio_pins

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
        main_cpp_dict = parse_gpio_pins()
        pin_def_dict = parse_nucleo_pindef_pins()

        #pin mapping json
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        # Load pin mappings from the config file
        with open(config_file, 'r') as f:
            pin_mappings = json.load(f)
        
        # Map the pin name to an integer pin number
        if main_cpp_dict[pinName] == "DigitalIn":
            nucleo_pin_number = pin_mappings["PowerBoard_to_nucleo_pin_mapping"][pin_def_dict[pinName]]
            pi_pin_number = pin_mappings["nucleo_to_pi_mapping"][f"{nucleo_pin_number}"]
        else:
            raise ValueError(f"Pin name '{pinName}' not found.")
        
        return pi_pin_number

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
        main_cpp_dict = parse_gpio_pins()
        pin_def_dict = parse_nucleo_pindef_pins()

        #pin mapping json
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        # Load pin mappings from the config file
        with open(config_file, 'r') as f:
            pin_mappings = json.load(f)
        
        # Map the pin name to an integer pin number
        if main_cpp_dict[pinName] == "DigitalOut":
            nucleo_pin_number = pin_mappings["PowerBoard_to_nucleo_pin_mapping"][pin_def_dict[pinName]]
            pi_pin_number = pin_mappings["nucleo_to_pi_mapping"][f"{nucleo_pin_number}"]
        else:
            raise ValueError(f"Pin name '{pinName}' not found.")

        return pi_pin_number

    #Constructor
    def __init__(self, pinName: str):
        self.pinName = pinName
        self.pinNumber = self.__PinValidate(pinName=pinName)
        self.pinObject = gpiozero.DigitalInputDevice(self.pinNumber)

    #Read function: returns a boolean 
    def read(self) -> bool:
        return self.pinObject.is_active


"""
AnalogOutput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Write (validate input based on established range)
"""

class AnalogOutput:
    #Validate the Pin Number
    #INPUT: self and pinName as a string
    #OUTPUT: returns the pin_number from mapping
    def __PinValidate(self, pinName: str) -> bool:
        main_cpp_dict = parse_gpio_pins()
        pin_def_dict = parse_nucleo_pindef_pins()

        #pin mapping json
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        # Load pin mappings from the config file
        with open(config_file, 'r') as f:
            pin_mappings = json.load(f)
        
        # Map the pin name to an integer pin number
        if main_cpp_dict[pinName] == "DigitalOut":
            nucleo_pin_number = pin_mappings["PowerBoard_to_nucleo_pin_mapping"][pin_def_dict[pinName]]
            pi_pin_number = pin_mappings["nucleo_to_pi_mapping"][f"{nucleo_pin_number}"]
        else:
            raise ValueError(f"Pin name '{pinName}' not found.")

        return pi_pin_number
    
    #Constructor
        #Active-High
        #Default Duty Cycle: 0
        #Default freq: 100 Hz ;)
    def __init__(self, pinName: str):
        self.pinName = pinName
        self.pinNumber = self.__PinValidate(pinName=pinName)
        self.pinObject = gpiozero.PWMOutputDevice(self.pinNumber)

    #Accepts values of [0,1]
    def set_duty_cycle(self, value: float):
        if 0.0 <= value <= 1.0:
            self.pinObject.value = value
        
        #else: do nothing
        
    #sets duty cycle to 1.0
    def on(self) -> None:
        self.pinObject.on()

    #sets duty cycle to 0.0
    def off(self) -> None:
        self.pinObject.off()



