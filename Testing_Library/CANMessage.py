#DBC Import
import cantools as ct
import os

# DBC_FILES are the 'definitions'/'mappings' files, they are not parseable yet.
dbc_files = os.listdir("./CAN-messages")
DBCs = [ct.db.load_file(f"./CAN-messages/{file}") for file in dbc_files if file.endswith(".dbc")]
# DBCs takes the files from DBC_FILES and turns each file into a DBC Object that has functions to access can msg types
# Function in our code depend on these definitions/configurations to get information on each type of can message.


#CANMessage Format on Raspberry Pi
class CanMessage:
    def __init__(self, name: str, id: int, signals: dict, timestamp: float):
        self.messageName = name
        self.messageId = id
        self.sigDict = signals
        self.timeStamp = timestamp
        
    #Encode is not working (returns an empty byte array)
    def encode_message(self) -> bytes:
        #Check whether name is in DBC files
        for db in DBCs:
            for msg in db.messages:
                if msg.name == self.messageName:
                    #Ensure full signal dictionary is present (append if not present)
                    for signal in msg.signals:
                        if signal not in self.sigDict:
                            self.sigDict.update({signal.name: 1.0})
                    #Encode using encode_message()
                    #print(msg.id)
                    encoded_message = db.encode_message(self.messageName, self.sigDict)
                    return encoded_message
        #Return None if not present in DBC files            
        print("Name was not present in DBC files")
        return None
         
         
    def getName(self):
        return self.messageName

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
        print("Decoded message was not associated")
        return None

    return CanMessage(name, id, decoded_message, timestamp)
    
