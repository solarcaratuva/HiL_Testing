#DBC Import
import cantools as ct
import os
import pprint

from CANMessage import CanMessage
import CANPi

import threading
import time

# DBC_FILES are the 'definitions'/'mappings' files, they are not parseable yet.
dbc_files = os.listdir("/home/solarcar/solarcar/HiL_Testing/Testing_Library/CAN-messages")
DBCs = [ct.db.load_file(f"/home/solarcar/solarcar/HiL_Testing/Testing_Library/CAN-messages/{file}") for file in dbc_files if file.endswith(".dbc")]
# DBCs takes the files from DBC_FILES and turns each file into a DBC Object that has functions to access can msg types
# Function in our code depend on these definitions/configurations to get information on each type of can message.

#CANBusDict => {(str) Message Type : [CANMessages] Instances of Message Type}

class CANBus:
    def __init__(self):
        self.stop_thread = False
        self.CANBusDict = {}
        #Instantiate CANBus using dbc files
        for db in DBCs:
            for msg in db.messages:
                #msg is of type CANMessage
                self.CANBusDict[msg.name] = []
        self.lock = threading.Lock()
        self.startReadThread()

    def printCANBus(self):
        for messageType, canMessage in self.CANBusDict.items():
            print(f'This is the CAN Message Type: {messageType} \t | \t These are the CAN Messages: {canMessage} ')
    
    def sendMessage(self, msg : CanMessage):
        CANPi.writeOut(msg)

    #Run infinite thread to read in CAN Messages
    def startReadThread(self):
        read_thread = threading.Thread(target=self.readMessages)
        read_thread.daemon = True
        try:
            read_thread.start()
        except ValueError as e:
            print(f"Caught the following exception: {e} \n Check whether the global dictionary is still locked.\n")
        
    def readMessages(self):
        with self.lock:
            while (not self.stop_thread):
                read_can_message = CANPi.readIn()
                if (read_can_message != None):
                    self.addToCANBus(read_can_message)
                #CHECK WHETHER A DELAY IS NEEDED OR NOT
                time.sleep(0.5)

    def stopReadThread(self):
        self.stop_thread = True

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
        self.CANBusDict[messageName] = []
