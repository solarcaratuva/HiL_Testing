import threading
import time

import can

import CANMessage
from CANMessage import CanMessage, DBCs

# Main CAN on the CANable 2.0. Nucleo RX PB5, TX PB6, standby PB4.
BITRATE = 250_000
CHANNEL = "can0"
UART_BAUD = 14400  # Rivanna3 mock only

_active = None


def _repo_root() -> str:
    try:
        import config
        return str(config.REPO_ROOT)
    except Exception:
        return ""


def uses_canable(repo_root: str | None = None) -> bool:
    root = _repo_root() if repo_root is None else repo_root
    return "rivanna3s" in root.lower()


def open_canable():
    return can.Bus(interface="socketcan", channel=CHANNEL, bitrate=BITRATE)


def clear_receive_queue() -> None:
    if _active is not None:
        _active.empty_for_reset()


def _payload(msg: CanMessage) -> bytes:
    framed = msg.encode_message()
    return framed[3:3 + framed[2]]


class CANBus:
    def __init__(self, bus=None, repo_root: str | None = None):
        global _active
        self.stop_thread = False
        self.discard = False
        self.CANBusDict = {msg.name: [] for db in DBCs for msg in db.messages}
        self.lock = threading.Lock()
        self.bus = None
        self.serial = None
        self.canable = bus is not None or uses_canable(repo_root)
        if self.canable:
            self.bus = bus if bus is not None else open_canable()
        else:
            import serial
            self.serial = serial.Serial(
                port="/dev/ttyAMA0",
                baudrate=UART_BAUD,
                timeout=10,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
        _active = self
        self._thread = threading.Thread(target=self.readMessages, daemon=True)
        self._thread.start()

    def close(self) -> None:
        self.stop_thread = True
        if self.bus is not None:
            try:
                self.bus.shutdown()
            except Exception:
                pass
        self._thread.join(timeout=1)

    def printCANBus(self):
        for messageType, canMessage in self.CANBusDict.items():
            print(f"This is the CAN Message Type: {messageType} \t | \t These are the CAN Messages: {canMessage} ")

    def sendMessage(self, msg: CanMessage):
        if self.canable:
            self.bus.send(can.Message(
                arbitration_id=msg.messageId & 0x7FF,
                data=_payload(msg),
                is_extended_id=False,
            ))
        else:
            self.serial.write(msg.encode_message())

    def readMessages(self):
        while not self.stop_thread:
            try:
                if self.canable:
                    self._read_can()
                else:
                    self._read_uart()
            except Exception:
                if self.stop_thread:
                    return
                time.sleep(0.01)

    def _read_can(self):
        frame = self.bus.recv(timeout=0.05)
        if frame is None or frame.is_error_frame or frame.is_remote_frame:
            return
        try:
            decoded = CANMessage.decode_message(
                frame.arbitration_id, bytes(frame.data), frame.timestamp or time.time()
            )
        except Exception:
            return
        with self.lock:
            if not self.discard:
                self.addToCANBus(decoded)

    def _read_uart(self):
        self.serial.reset_input_buffer()
        response = self.serial.read(2)
        id_data = int.from_bytes(response[0:2], "big")
        response = self.serial.read(1)
        length_data = int.from_bytes(response, "big")
        if 0 <= length_data <= 8:
            response = self.serial.read(length_data)
        try:
            read_can_message = CANMessage.decode_message(id_data, response, int(time.time()))
        except Exception:
            read_can_message = None
        with self.lock:
            if read_can_message is not None and not self.discard:
                self.addToCANBus(read_can_message)
        time.sleep(0.01)

    def addToCANBus(self, CANMessageToAdd: CanMessage):
        if CANMessageToAdd.getName() not in self.CANBusDict:
            raise ValueError("CAN Message type was not found in the DBC files.")
        self.CANBusDict[CANMessageToAdd.getName()].append(CANMessageToAdd)

    def getReceivedMessages(self, messageName: str):
        with self.lock:
            can_messages = self.CANBusDict.get(messageName)
            if messageName in self.CANBusDict:
                self.CANBusDict[messageName] = []
            return can_messages

    def clearReceivedMessages(self, messageName: str):
        with self.lock:
            self.CANBusDict[messageName] = []

    def empty_for_reset(self):
        # ponytail: 50ms drop window; filter by id if a live bus must keep other frames
        with self.lock:
            self.discard = True
            for name in self.CANBusDict:
                self.CANBusDict[name] = []
        time.sleep(0.05)
        with self.lock:
            for name in self.CANBusDict:
                self.CANBusDict[name] = []
            self.discard = False
