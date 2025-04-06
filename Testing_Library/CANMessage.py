#DBC Import
import cantools as ct
import os
import pprint

# DBC_FILES are the 'definitions'/'mappings' files, they are not parseable yet.
dbc_files = os.listdir("/home/solarcar/solarcar/HiL_Testing/Testing_Library/CAN-messages")
DBCs = [ct.db.load_file(f"/home/solarcar/solarcar/HiL_Testing/Testing_Library/CAN-messages/{file}") for file in dbc_files if file.endswith(".dbc")]
# DBCs takes the files from DBC_FILES and turns each file into a DBC Object that has functions to access can msg types
# Function in our code depend on these definitions/configurations to get information on each type of can message.

#CANMessage Format on Raspberry Pi
class CanMessage:
    def __init__(self, name: str, id: int, signals: dict, timestamp: float):
        self.messageName = name
        self.messageId = id
        self.sigDict = signals
        self.timeStamp = timestamp
        
    def encode_message(self) -> bytes:
        found = False
        #Check whether name is in DBC files
        for db in DBCs:
            for msg in db.messages:
                if msg.name == self.messageName:
                    found = True
                    #Ensure full signal dictionary is present (append if not present)
                    for signal in msg.signals:
                        if signal not in self.sigDict:
                            self.sigDict.update({signal.name: 1.0})
                    found_db = db 
                            
        if (not found):
            #Return None if not present in DBC files            
            raise Exception("Name was not present in DBC files")
            return None
            
        #Expected Encoded Format --> ID (First 2 Bytes), Message (All Remaining Bytes)
        data_encoded = found_db.encode_message(self.messageName, self.sigDict)
        encoded_message = self.messageId.to_bytes(2, 'big') + len(data_encoded).to_bytes(1, 'big') + data_encoded
        #add id to first two bytes of encoded_message
        return encoded_message
        
    def getName(self):
        return self.messageName
        
    def __str__(self):
        string = f"CAN Type: {self.messageName}  |  CAN ID: {self.messageId}  \nDATA: {pprint.pformat(self.sigDict)}\n"
        return string

@staticmethod
def decode_message(id: int, data: bytes, timestamp: float) -> CanMessage:
    """
    Decodes the message using previously generated DBCs object

    @param id: The messages's ID as an int
    @param data: The data as a python byte object
    @param timestamp: timestamp of the message stored as float time from start time.

    @return: A CANmessage object (defined above). In sigDict, Signals are the keys and decoded values are the values. Returns None if the message type is not found in the DBC files.
    """
    name = None
    # id = int(id_hex, 16) Old code, kept for reference
    # data = bytes.fromhex(data_hex.replace("0x", ""))
    data += b'\x00' * 8  # adding padding

    decoded_message = None  # dictionary of signals to return

    for db in DBCs:
        for msg in db.messages:
            if msg.frame_id == id:
                name = msg.name
                decoded_message = db.decode_message(id, data)
                break
        if decoded_message is not None:
            break

    # if decoded message was not associated with a definition from DBCs, return None
    if decoded_message is None:
        raise Exception("Decoded message was not associated")
        return None

    return CanMessage(name, id, decoded_message, timestamp)
    
