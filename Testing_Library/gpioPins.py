import gpiozero
import time
import Server.config as config

#IMPORTANT NOTES:
#Constructors use default values from gpiozero
#DigitalOutput: Active High, Intitial Value-0, 
#DigitalInput: Pulldown resistor, Active High, No bounce compensation

DEBUG_SKIP_PIN_VALIDATION = True

def PinValidate(pinName: str, pinType: str) -> int:
    """SHOULD NOT BE CALLED BY TESTS. Validate the Pin Number.

    @param pinName: The nice pin name (ex. THROTTLE_PEDAL) on the Nucleo as a string
    @param pinType: The type of pin as a string
    @return: The pin number on the Pi as an integer"""

    if DEBUG_SKIP_PIN_VALIDATION:
        return int(pinName)

    if not isinstance(pinName, str):
        raise TypeError("Pin name must be a string")

    if pinName not in config.PIN_NAMES_MAP:
        raise ValueError(f"Pin name '{pinName}' not declared in pindef.h")
    nucleo_pin_name = config.PIN_NAMES_MAP[pinName]

    if nucleo_pin_name not in config.SERVER_CONFIG["nucleo_pin_name_to_number_mapping"]:
        raise ValueError(f"Nucleo pin name '{nucleo_pin_name}' not mapped to a pin number in server_config.json")
    nucleo_pin_number = config.SERVER_CONFIG["nucleo_pin_name_to_number_mapping"][nucleo_pin_name]

    if str(nucleo_pin_number) not in config.SERVER_CONFIG["nucleo_to_pi_mapping"]:
        raise ValueError(f"Nucleo pin number '{nucleo_pin_number}' not mapped to a Pi pin in server_config.json")
    pi_pin_number = config.SERVER_CONFIG["nucleo_to_pi_mapping"][str(nucleo_pin_number)]

    pin_types_map = {"DigitalIn": "DigitalOut", "DigitalOut": "DigitalIn", "AnalogOut": "AnalogIn"} # key: Pi pin types, values: appropriate Nucleo pin type
    if pin_types_map[pinType] != config.PIN_TYPES_MAP[pinName]:
        raise ValueError(f"'{pinName}' is a {pinType} pin on the Pi, which can't properly connect to a {config.PIN_TYPES_MAP[pinName]} Nucleo pin")
    
    return pi_pin_number

def reset_all_pins() -> None:
    pass #TODO

def reset_nucleo() -> None:
    pinObject = gpiozero.DigitalOutputDevice(2)
    pinObject.on()
    time.sleep(1)
    pinObject.off()



class DigitalOutput:
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

    def __init__(self, pinName: str):
        self.pinName = pinName
        self.pinNumber = PinValidate(pinName, "DigitalOutput")
        self.pinObject = gpiozero.DigitalOutputDevice(self.pinNumber)

    def write(self, state: bool) -> None:
        """Writes to the digital pin"""
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
        return self.pinObject.value == 1
        


class DigitalInput:
    """"
    DigitalInput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Read : bool
    """

    def __init__(self, pinName: str):
        self.pinName = pinName
        self.pinNumber = PinValidate(pinName, "DigitalInput")
        self.pinObject = gpiozero.DigitalInputDevice(self.pinNumber)

    def read(self) -> bool:
        return self.pinObject.is_active
    

class AnalogOutput:
    """
    AnalogOutput class
    Parameters:
        Pinname : String (same style as pinmap.h; validate pin name)
    Methods:
        Write (validate input based on established range)
    """
    
    #Constructor
        #Active-High
        #Default Duty Cycle: 0
        #Default freq: 100 Hz ;)
    def __init__(self, pinName: str):
        self.pinName = pinName
        self.pinNumber = PinValidate(pinName, "AnalogOutput")
        self.pinObject = gpiozero.PWMOutputDevice(self.pinNumber, frequency=5000)

    #Accepts values of [0,1]
    def write(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError("Value must be a float")
        if value < 0 or value > 1:
            raise ValueError("Value must be between 0 and 1")
        
        self.pinObject.value = value
        time.sleep(0.02) # wait 20ms for the capacitor in the lowpass filter to charge / discharge as needed
        
    def read(self) -> float:
        return self.pinObject.value
        
    #sets duty cycle to 1.0
    def on(self) -> None:
        self.pinObject.on()

    #sets duty cycle to 0.0
    def off(self) -> None:
        self.pinObject.off()