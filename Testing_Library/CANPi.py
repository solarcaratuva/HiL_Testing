#Goal of CANPi: use PySerial class to send a receive data with NUCLEO Board (mock CAN)
import serial
import time
import CANMessage

mbed_serial = serial.Serial(
    #Define the UART Pin Number (PIN 8 tx and PIN 10 rx)
    port = '/dev/serial0',
    baudrate=9600,
    timeout=10,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

#'CAN' Read Using PySerial
def readIn() -> CANMessage:
    try:
        #CURRENTLY: Message format: 2 bytes of ID, 1 byte of length, rest data
        #mbed_serial.reset_input_buffer()
        print("HERE")
        print(f'THIS IS WHAT I"M READING IN: {mbed_serial.read(2)}')
        response = mbed_serial.read(2)
        id_data = int.from_bytes(response[0:2], "big")

        response = mbed_serial.read(1)
        length_data = int.from_bytes(response[0], "big")

        if 0 <= length_data <= 8:
            response = mbed_serial.read(length_data)
        #if (response != None):
        print(f"This is the raw byte being read in: {response}\n\n\n")

        CANData = CANMessage.decode_message(id_data, response, int(time.time()))
        return CANData
            
        #OLD CODE:
        # response = mbed_serial.readline()
        # #print(f'READ ENCODED MESSAGE: {response}\n')
        # #Convert message into CAN Format using CANMessage
        # id_data = int.from_bytes(response[0:2], "big")

        
    except serial.SerialException:
        print("Serial Exception Error")

    except serial.SerialTimeoutException:
        print("Serial Timeout Error")
    except Exception as e:
        print(e)    
        
#'CAN' Write Using PySerial: accepts CANMessage tx_data
def writeOut(tx_data):
    #print(f'WRITING TO PIN: {tx_data}') 
    mbed_serial.write(tx_data.encode_message())


#Use this to test encoding (raspberry pi to nucleo)
def defaultCANEncodeTest():
    testCAN = CANMessage.CanMessage("MotorCommands", 0x200, {}, 0)
    writeOut(testCAN)
    data = readIn()
    #print(data)

#Use this to test decoding (nucleo to raspberry pi)
def defaultCANDecodeTest():
    while (True):   
        try: 
            #print("READING IN CAN MESSAGE")
            data = readIn()
            time.sleep(1)
            print(data)
        except KeyboardInterrupt:
            #print("Exiting Program")
            break
            
