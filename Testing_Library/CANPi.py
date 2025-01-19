#Goal of CANPi: use PySerial class to send a receive data with NUCLEO Board (mock CAN)
import serial
import time
import CANMessage

mbed_serial = serial.Serial(
    #Define the UART Pin Number (PIN 8 tx and PIN 10 rx)
    port = '/dev/serial0',
    baudrate=9600,
    timeout=5,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

#'CAN' Read Using PySerial
def readIn():
    try:
        response = mbed_serial.readline()
        print(f'Encoded CAN Message: {response}')
        #Convert message into CAN Format using CANMessage
        #id_data = int.from_bytes(response[0:2], "big")
        CANData = CANMessage.decode_message(0x325, response, int(time.time()))
        return CANData
    except serial.SerialException:
        print("Serial Exception Error")

    except serial.SerialTimeoutException:
        print("Serial Timeout Error")
        
        #'CAN' Write Using PySerial
def writeOut(tx_data):
    print(f'WRITING TO PIN: {tx_data}') 
    mbed_serial.write(tx_data)
    #mbed_serial.write(tx_data.encode())
    
    
testCAN = CANMessage.CanMessage("MotorControllerPowerStatus", 0x325, {}, 0)
writeOut(testCAN.encode_message())
while (True):   
    try: 
        
        time.sleep(3)
        data = readIn()
        print(f'THE RASPBERRY PI READ AS CAN THE FOLLOWING MESSAGE: {data}\n')
    except KeyboardInterrupt:
        print("Exiting Program")
        break
    # print(f'READING FROM NUCLEO: {readIn()}\n')
