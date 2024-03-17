from Exceptions import *
import pinLookup as plu

class Pin:
    def __init__(this, pinName: str, board: str) -> None:
        pass

    def setPin(this, state: float|bool) -> None:
        pass

    def getPin(this) -> float|bool:
        pass

def setup(env_data: dict | str) -> None:
    if env_data == "mock":
        global mock
        mock = True
        return
    # included data: pin map, ST Link to board map
    pass
