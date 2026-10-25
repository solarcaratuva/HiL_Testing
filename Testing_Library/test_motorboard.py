"""MotorBoard: one run, pedal + regen command, both Pico values, motor command."""
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


class _Pin:
    def __init__(self, pin, *args, **kwargs):
        self.pin = pin
        self.value = 0

    def on(self):
        self.value = 1

    def off(self):
        self.value = 0


gpiozero = types.ModuleType("gpiozero")
gpiozero.DigitalInputDevice = _Pin
gpiozero.DigitalOutputDevice = _Pin
gpiozero.PWMOutputDevice = _Pin
sys.modules["gpiozero"] = gpiozero

import config
from CANMessage import CanMessage, decode_message

config.SERVER_CONFIG = json.loads((SERVER / "server_config.json").read_text())
config.REPO_ROOT = str(R3S)


class _Session:
    def __init__(self, *args, **kwargs):
        pass

    def read(self):
        return (0, 255)

    def close(self):
        pass


class _Bus:
    sent = []

    def __init__(self, bus=None, repo_root=None):
        pass

    def sendMessage(self, msg):
        _Bus.sent.append(msg)

    def close(self):
        pass

    def getReceivedMessages(self, name):
        if name != "MotorCommands":
            return []
        return [CanMessage("MotorCommands", 0xC8, {
            "throttle": 0, "regen_braking": 255, "regen_drive": 1,
        }, 1.0)]


def main():
    import MotorInterfaceTest as mit
    assert mit.THROTTLE_ADDR == 0x2F and mit.REGEN_ADDR == 0x2E
    mit.MotorInterfaceTest = _Session
    text = (R3S / "MotorBoard" / "tests" / "test.py").read_text()
    assert "I2C_TEST_MODE" not in text and "AnalogOutput" not in text
    assert text.count("def test_") == 2 and ".read()" in text
    import importlib.util
    spec = importlib.util.spec_from_file_location("motor_tests", R3S / "MotorBoard" / "tests" / "test.py")
    motor_tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(motor_tests)
    assert motor_tests.expected_regen(0) == 255
    frame = CanMessage("MotorCommands", 0xC8, {"throttle": 0, "regen_braking": 255, "regen_drive": 1}, 1.0)
    data = frame.encode_message()[3:]
    assert data[0] == 255 and data[2] == 0 and data[3] & 0x04 == 0x04
    decoded = decode_message(0xC8, data, 1.0)
    assert int(decoded.sigDict["throttle"]) == 0
    assert int(decoded.sigDict["regen_braking"]) == 255
    assert int(decoded.sigDict["regen_drive"]) == 1
    boards = json.loads((R3S / "hil_config.json").read_text())["boards"]
    assert "MotorBoard" in boards
    import CANBus
    CANBus.CANBus = _Bus
    CANBus.clear_receive_queue = lambda: None
    suite = unittest.defaultTestLoader.discover(str(R3S / "MotorBoard" / "tests"), pattern="*.py")
    assert suite.countTestCases() == 2
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    assert result.wasSuccessful()
    assert [m.messageName for m in _Bus.sent] == ["PedalStatus", "DashboardCommands"]
    assert _Bus.sent[0].messageId == 0x1F4 and _Bus.sent[0].sigDict["throttle_pedal"] == 0
    assert _Bus.sent[1].messageId == 0x12C and _Bus.sent[1].sigDict["regen_en"] == 1
    print("ok")


if __name__ == "__main__":
    main()
