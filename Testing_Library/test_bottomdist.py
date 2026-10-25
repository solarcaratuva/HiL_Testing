"""BottomDist throttle wiper: PA3, old thresholds, pedal status, no Pico."""
import json
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE.parent / "Server"
R3S = HERE.parents[1] / "Rivanna3S"
sys.path.insert(0, str(SERVER))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(R3S / "BottomDist" / "tests"))


class _Pin:
    pwm = []
    outputs = []

    def __init__(self, pin, *args, **kwargs):
        self.pin = pin
        self.value = 0

    def on(self):
        self.value = 1

    def off(self):
        self.value = 0


class _Pwm(_Pin):
    def __init__(self, pin, *args, **kwargs):
        super().__init__(pin, *args, **kwargs)
        _Pin.pwm.append(pin)


class _Out(_Pin):
    def __init__(self, pin, *args, **kwargs):
        super().__init__(pin, *args, **kwargs)
        _Pin.outputs.append(pin)


gpiozero = types.ModuleType("gpiozero")
gpiozero.DigitalInputDevice = _Pin
gpiozero.DigitalOutputDevice = _Out
gpiozero.PWMOutputDevice = _Pwm
sys.modules["gpiozero"] = gpiozero

import config
from CANMessage import CanMessage

config.SERVER_CONFIG = json.loads((SERVER / "server_config.json").read_text())
config.REPO_ROOT = str(R3S)


class _Bus:
    sent = []
    pedal = [0, 85, 170]

    def __init__(self, bus=None, repo_root=None):
        pass

    def sendMessage(self, msg):
        _Bus.sent.append(msg)

    def close(self):
        pass

    def getReceivedMessages(self, name):
        if name == "PedalStatus" and _Bus.pedal:
            value = _Bus.pedal.pop(0)
            return [CanMessage("PedalStatus", 0x1F4, {"throttle_pedal": value, "brake_pedal": 0}, 0.0)]
        return []


def main():
    import bottom_tests
    assert bottom_tests.throttle_counts(0.1) == 0
    assert bottom_tests.throttle_counts(0.5) == 85
    assert bottom_tests.throttle_counts(0.75) == 170
    text = (R3S / "BottomDist" / "tests" / "test.py").read_text()
    assert "MotorInterface" not in text and "0x2F" not in text and "0x2E" not in text
    import NucleoPinParser
    assert NucleoPinParser.parse_nucleo_pindef_pins("BottomDist")["THROTTLE_WIPER"] == "PA_3"
    assert NucleoPinParser.parse_gpio_pins("BottomDist")["THROTTLE_WIPER"] == "AnalogIn"
    boards = json.loads((R3S / "hil_config.json").read_text())["boards"]
    assert "BottomDist" in boards
    data = CanMessage("PedalStatus", 0x1F4, {"throttle_pedal": 85}, 0.0).encode_message()[3:]
    assert data[0] == 85 and data[1] & 0x0F == 0
    import CANBus
    CANBus.CANBus = _Bus
    CANBus.clear_receive_queue = lambda: None
    suite = unittest.defaultTestLoader.discover(str(R3S / "BottomDist" / "tests"), pattern="*.py")
    assert suite.countTestCases() == 2
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    assert result.wasSuccessful()
    assert _Bus.sent == []
    assert _Pin.pwm == [3]
    assert _Pin.outputs == [14, 14]
    print("ok")


import importlib.util
_spec = importlib.util.spec_from_file_location(
    "bottom_tests", R3S / "BottomDist" / "tests" / "test.py")
bottom_tests = importlib.util.module_from_spec(_spec)

if __name__ == "__main__":
    _spec.loader.exec_module(bottom_tests)
    sys.modules["bottom_tests"] = bottom_tests
    main()
