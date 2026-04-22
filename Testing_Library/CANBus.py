#DBC Import
import cantools as ct
import os
import pprint
import serial
import CANMessage

from CANMessage import CanMessage, DBCs

import threading
import time

mbed_serial = serial.Serial(
    #Define the UART Pin Number (PIN 8 tx and PIN 10 rx)
    port = '/dev/ttyAMA0',
    baudrate=14400,
    timeout=10,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)

#CANBusDict => {(str) Message Type : [CANMessages] Instances of Message Type}

# dictionary for all existing can bus
BUS_ID = {
    "Main": 0,
    "Power": 1 # ADD MORE AS NECESSAYR
}

# reg
BUS_OBJECTS = {}


class CANBus:
    def __init__(self, bus_name: str):
        # add in a new field to hold canbus id (1 byte - which canbus?)
        if bus_name not in BUS_ID:
            raise ValueError(f"Unknown CAN bus: {bus_name}")
        self.bus_name = bus_name
        self.bus_id = BUS_ID[bus_name]
        self.stop_thread = False
        self.CANBusDict = {}
        #Instantiate CANBus using dbc files
        for db in DBCs:
            for msg in db.messages:
                #msg is of type CANMessage
                self.CANBusDict[msg.name] = list()
        self.lock = threading.Lock()
        BUS_OBJECTS[self.bus_id] = self
        # self.startReadThread()  # doubel check if still need this for reading threads if new thread is implemented for routing

    # for routing messages in pi for canbus
    def handleRoutedMessage(self, read_can_message):
        print(f"Routed {read_can_message.getName()} to bus {self.bus_name}")
        self.addToCANBus(read_can_message)

    def printCANBus(self):
        for messageType, canMessage in self.CANBusDict.items():
            print(f'This is the CAN Message Type: {messageType} \t | \t These are the CAN Messages: {canMessage} ')
    
    def sendMessage(self, msg : CanMessage):
        bus_byte = self.bus_id.to_bytes(1, 'big')
        mbed_serial.write(bus_byte + msg.encode_message())

    #Run infinite thread to read in CAN Messages
    def startReadThread(self):
        read_thread = threading.Thread(target=self.readMessages)
        read_thread.daemon = True
        try:
            read_thread.start()
        except ValueError as e:
            print(f"Caught the following exception: {e} \n Check whether the global dictionary is still locked.\n")
        
    def readMessages(self):
        while (not self.stop_thread):
            with self.lock:
                #CURRENTLY: Message format: 1 byte bus identifier, 2 bytes of ID, 1 byte of length, rest data
                mbed_serial.reset_input_buffer()

                # new readMessages data for 1 byte bus identifier
                bus_response = mbed_serial.read(1)
                bus_data = int.from_bytes(bus_response, "big")

                response = mbed_serial.read(2)       
                id_data = int.from_bytes(response[0:2], "big")
                response = mbed_serial.read(1)
                length_data = int.from_bytes(response, "big")

                if 0 <= length_data <= 8:
                    response = mbed_serial.read(length_data)

                read_can_message = CANMessage.decode_message(id_data, response, int(time.time()))
                if (read_can_message != None):
                    self.addToCANBus(read_can_message)
                    
                time.sleep(0.01)

    def addToCANBus(self, CANMessageToAdd : CanMessage):
        #Check whether can message name is in dbc files
        found = False
        for messageType in self.CANBusDict.keys():
            if (messageType == CANMessageToAdd.getName()):
                found = True
        if (not found):
            raise ValueError("CAN Message type was not found in the DBC files.")
        #Add to CANBus
        self.CANBusDict.get(CANMessageToAdd.getName()).append(CANMessageToAdd)

    def getReceivedMessages(self, messageName : str):
        can_messages = self.CANBusDict.get(messageName)
        self.clearReceivedMessages(messageName)
        return can_messages

	#Clear only for that specific message type
    def clearReceivedMessages(self, messageName : str):
        self.CANBusDict[messageName] = list()


def routeMessages():
    while True:
        # reads from serial - 1 byte bus, 2 bytes id, payload, byte length
        bus_response = mbed_serial.read(1)
        if len(bus_response) != 1:
            continue
        bus_data = int.from_bytes(bus_response, "big")

        response = mbed_serial.read(2)
        if len(response) != 2:
            continue
        id_data = int.from_bytes(response[0:2], "big")

        response = mbed_serial.read(1)
        if len(response) != 1:
            continue
        length_data = int.from_bytes(response, "big")

        if not (0 <= length_data <= 8):
            continue

        response = mbed_serial.read(length_data)
        if len(response) != length_data:
            continue

        read_can_message = CANMessage.decode_message(id_data, response, int(time.time()))
        if read_can_message is None:
            continue

        if bus_data in BUS_OBJECTS:
            BUS_OBJECTS[bus_data].handleRoutedMessage(read_can_message)
        else:
            print(f"Unknown bus id {bus_data}")

def startRoutingThread():
    # start one routing threda
    read_thread = threading.Thread(target=routeMessages)
    read_thread.daemon = True
    read_thread.start()


canBus = CANBus("Main")
print(canBus.bus_name)
print(canBus.bus_id)