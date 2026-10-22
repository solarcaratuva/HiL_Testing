"""TopDist lamp and strobe cases: CAN commands, PA1/PC2, sheet pins."""
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE.parent / "Server"
R3S = HERE.parents[1] / "Rivanna3S"
R3 = Path("/Users/abhinavpappu/Documents/Projects/SolarCar/Rivanna3")
sys.path.insert(0, str(SERVER))
sys.path.insert(0, str(HERE))


class _Pin:
    inputs = []
    outputs = []

    def __init__(self, pin, *args, **kwargs):
        self.pin = pin
        self.value = 0
        self.n = 0

    def on(self):
        self.value = 1

    def off(self):
        self.value = 0

    @property
    def is_active(self):
        self.n += 1
        return self.n % 2 == 0


class _In(_Pin):
    def __init__(self, pin, *args, **kwargs):
        super().__init__(pin, *args, **kwargs)
        _Pin.inputs.append(pin)


class _Out(_Pin):
    def __init__(self, pin, *args, **kwargs):
        super().__init__(pin, *args, **kwargs)
        _Pin.outputs.append(pin)


gpiozero = types.ModuleType("gpiozero")
gpiozero.DigitalInputDevice = _In
gpiozero.DigitalOutputDevice = _Out
gpiozero.PWMOutputDevice = _Out
sys.modules["gpiozero"] = gpiozero

import config
import NucleoPinParser
from CANMessage import CanMessage, decode_message

config.SERVER_CONFIG = json.loads((SERVER / "server_config.json").read_text())


class _Bus:
    sent = []

    def __init__(self, bus=None, repo_root=None):
        pass

    def sendMessage(self, msg):
        _Bus.sent.append(msg)

    def close(self):
        pass

    def getReceivedMessages(self, name):
        return []


def _parser_keeps_nucleo_block():
    with tempfile.TemporaryDirectory() as tmp:
        inc = Path(tmp) / "PowerBoard" / "include"
        src = Path(tmp) / "PowerBoard" / "src"
        inc.mkdir(parents=True)
        src.mkdir()
        (inc / "pindef.h").write_text(
            "#ifdef TARGET_NUCLEO_F413ZH\n#define LEFT_TURN_OUT PC_10\n"
            "#else\n#define ONLY_OUTSIDE PA_9\n#endif\n"
        )
        (src / "main.cpp").write_text("DigitalOut left_turn_signal(LEFT_TURN_OUT);\n")
        config.REPO_ROOT = tmp
        pins = NucleoPinParser.parse_nucleo_pindef_pins("PowerBoard")
        assert pins == {"LEFT_TURN_OUT": "PC_10"}
        kinds = NucleoPinParser.parse_gpio_pins("PowerBoard")
        assert kinds["LEFT_TURN_OUT"] == "DigitalOut"

    config.REPO_ROOT = str(R3)
    live = NucleoPinParser.parse_nucleo_pindef_pins("PowerBoard")
    assert live["LEFT_TURN_OUT"] == "PC_10"
    assert live["BMS_STROBE_OUT"] == "PA_3"
    assert live["THROTTLE_WIPER"] == "PA_6"


def _frames():
    turn = CanMessage("DashboardCommands", 0x12C, {"left_turn_signal": 1}, 1.0)
    raw = turn.encode_message()
    assert raw[:2] == (0x12C).to_bytes(2, "big") and raw[2] == 1 and raw[3] == 0x02
    old = CanMessage("DashboardCommands", 0x300, {"left_turn_signal": 1}, 1.0)
    assert old.encode_message()[3] == 0x02
    fault = CanMessage("BpsError", 0x3AA, {"internal_cell_communication_fault": 1}, 1.0)
    data = fault.encode_message()[3:]
    assert len(data) == 4 and data[0] == 1
    assert decode_message(0x3AA, data, 1.0).sigDict["internal_cell_communication_fault"] == 1


def main():
    _parser_keeps_nucleo_block()
    _frames()
    config.REPO_ROOT = str(R3S)
    boards = json.loads((R3S / "hil_config.json").read_text())["boards"]
    assert "TopDist" in boards
    import CANBus
    import gpioPins
    CANBus.CANBus = _Bus
    CANBus.clear_receive_queue = lambda: None
    suite = unittest.defaultTestLoader.discover(
        str(R3S / "TopDist" / "tests"), pattern="*.py")
    assert suite.countTestCases() == 3
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    assert result.wasSuccessful()
    names = [msg.messageName for msg in _Bus.sent]
    assert names == ["BpsError", "DashboardCommands"]
    assert _Bus.sent[0].messageId == 0x3AA
    assert _Bus.sent[1].messageId == 0x12C
    assert _Bus.sent[1].sigDict["left_turn_signal"] == 1
    assert _Pin.inputs == [34, 1]
    assert _Pin.outputs == [14, 14, 14]
    text = (R3S / "TopDist" / "tests" / "test.py").read_text()
    assert "DigitalOutput" not in text and "LEFT_TURN_IN" not in text
    try:
        gpioPins.PinValidate("NOT_ON_SHEET", "DigitalInput")
        raise SystemExit("unknown pin drove a GPIO")
    except ValueError:
        pass
    print("ok")


if __name__ == "__main__":
    main()
