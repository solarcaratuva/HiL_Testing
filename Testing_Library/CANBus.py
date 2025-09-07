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

class CANBus:
    def __init__(self):
        self.stop_thread = False
        self.CANBusDict = {}
        #Instantiate CANBus using dbc files
        for db in DBCs:
            for msg in db.messages:
                #msg is of type CANMessage
                self.CANBusDict[msg.name] = list()
        self.lock = threading.Lock()
        self.startReadThread()

    def printCANBus(self):
        for messageType, canMessage in self.CANBusDict.items():
            print(f'This is the CAN Message Type: {messageType} \t | \t These are the CAN Messages: {canMessage} ')
    
    def sendMessage(self, msg : CanMessage):
        mbed_serial.write(msg.encode_message())

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
                #CURRENTLY: Message format: 2 bytes of ID, 1 byte of length, rest data
                mbed_serial.reset_input_buffer()

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
