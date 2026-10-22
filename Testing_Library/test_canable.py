import sys
import time
import types

import can

cfg = types.ModuleType("config")
cfg.REPO_ROOT = ""
sys.modules["config"] = cfg

import CANBus
import CANPi
from CANMessage import CanMessage


def bps():
    return CanMessage("BPSError", 0x106, {"internal_communications_fault": 1}, 1.0)


def test_open_bitrate():
    seen = {}

    class Fake:
        def __init__(self, *args, **kwargs):
            seen.update(kwargs)

    real = CANBus.can.Bus
    CANBus.can.Bus = Fake
    try:
        CANBus.open_canable()
    finally:
        CANBus.can.Bus = real
    assert seen["interface"] == "socketcan" and seen["channel"] == "can0"
    assert seen["bitrate"] == CANBus.BITRATE == 250_000


def test_rivanna3s_skips_uart():
    seen = {}

    class Fake:
        def __init__(self, *args, **kwargs):
            seen.update(kwargs)

        def recv(self, timeout=None):
            time.sleep(0.01)
            return None

        def send(self, msg):
            seen["sent"] = msg

        def shutdown(self):
            pass

    import serial
    real_bus, real_serial = CANBus.can.Bus, serial.Serial
    CANBus.can.Bus = Fake

    def boom(*args, **kwargs):
        raise AssertionError("UART opened")

    serial.Serial = boom
    cfg.REPO_ROOT = "/home/solarcar/solarcar/Rivanna3s"
    bus = CANBus.CANBus()
    try:
        msg = bps()
        framed = msg.encode_message()
        bus.sendMessage(msg)
        assert seen["bitrate"] == 250_000
        assert bytes(seen["sent"].data) == framed[3:3 + framed[2]]
        assert bytes(seen["sent"].data) != framed
        try:
            CANPi.writeOut(msg)
            raise AssertionError("UART write accepted")
        except RuntimeError:
            pass
    finally:
        bus.close()
        CANBus.can.Bus = real_bus
        serial.Serial = real_serial


def test_exchange_and_reset():
    host = can.Bus(interface="virtual", channel="issue03")
    peer = can.Bus(interface="virtual", channel="issue03")
    bus = CANBus.CANBus(bus=host)
    try:
        msg = bps()
        payload = CANBus._payload(msg)
        bus.sendMessage(msg)
        rx = peer.recv(timeout=1)
        assert rx.arbitration_id == 0x106
        assert bytes(rx.data) == payload

        peer.send(can.Message(arbitration_id=0x106, data=payload, is_extended_id=False))
        deadline = time.time() + 1
        while time.time() < deadline and not bus.CANBusDict["BPSError"]:
            time.sleep(0.02)
        assert bus.CANBusDict["BPSError"][0].sigDict["internal_communications_fault"] == 1

        CANBus.clear_receive_queue()
        assert bus.getReceivedMessages("BPSError") == []
    finally:
        bus.close()
        host.shutdown()
        peer.shutdown()


def test_rivanna3_keeps_uart():
    import serial

    class FakeSerial:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.wrote = None
            FakeSerial.instance = self

        def read(self, n):
            time.sleep(0.02)
            return b"\x00" * n

        def reset_input_buffer(self):
            pass

        def write(self, data):
            self.wrote = data

    real = serial.Serial
    serial.Serial = FakeSerial
    cfg.REPO_ROOT = "/home/solarcar/solarcar/Rivanna3"
    CANPi.mbed_serial = None
    bus = CANBus.CANBus()
    try:
        msg = bps()
        bus.sendMessage(msg)
        assert bus.canable is False
        assert FakeSerial.instance.kwargs["baudrate"] == 14400
        assert FakeSerial.instance.wrote[:3] == msg.encode_message()[:3]
        CANPi.mbed_serial = None
        CANPi.writeOut(msg)
        assert FakeSerial.instance.kwargs["baudrate"] == 14400
    finally:
        bus.close()
        serial.Serial = real


if __name__ == "__main__":
    test_open_bitrate()
    test_rivanna3s_skips_uart()
    test_exchange_and_reset()
    test_rivanna3_keeps_uart()
    print("ok")
