#DBC Import
import cantools as ct
import os
import pprint
import CANMessage

# DBC_FILES are the 'definitions'/'mappings' files, they are not parseable yet.
dbc_files = os.listdir("/home/solarcar/HiL_Testing/Testing_Library/CAN-messages")
DBCs = [ct.db.load_file(f"/home/solarcar/HiL_Testing/Testing_Library/CAN-messages/{file}") for file in dbc_files if file.endswith(".dbc")]
# DBCs takes the files from DBC_FILES and turns each file into a DBC Object that has functions to access can msg types
# Function in our code depend on these definitions/configurations to get information on each type of can message.

#CANBusDict => {(CANMessage) Message Type : [CANMessages] Instances of Message Type}

class CANBus:
    def __init__(self):
        self.CANBusDict = {}
        #Instantiate CANBus using dbc files
        for db in DBCs:
            for msg in db.messages:
                #msg is of type CANMessage
                CANBusDict[msg] = None

    def printCANBus():
        for messageType, canMessages in self.AllCANMessages.items():
            print(f'This is the CAN Message Type: {messageType} \t | \t These are the CAN Messages: {canMessages} ')
    
    def addToCANBus(CANMessageToAdd : CANMessage):
        #Check whether can message name is in dbc files
        found = False
        for messageType in self.CANBusDict.keys():
            if (messageType.getName() == CANMessageToAdd.getName()):
                found = True
        if (not found){
            raise ValueError("CAN Message type was not found in the DBC files.")
        }
        #Add to CANBus
        self.CANBusDict.get(CANMessage).append(CANMessageToAdd)

    def clear():
        self.CANBusDict = {}