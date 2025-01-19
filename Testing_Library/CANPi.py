#Goal of CANPi: use PySerial class to send a receive data with NUCLEO Board (mock CAN)
import serial
import time
import CANMessage

mbed_serial = serial.Serial(
    #Define the UART Pin Number (PIN 8 tx and PIN 10 rx)
    port = '/def/serial0',
    baudrate=9600,
    timeout=5,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

#'CAN' Read Using PySerial
def readIn():
    try:
        response = mbed_serial.readline().decode().strip()
        #Convert message into CAN Format using CANMessage
        CANData = CANMessage.decode_message(response[0:2], response[2:], int(time.time()))
        return CANData
    except serial.SerialException:
        print("Serial Exception Error")

    except serial.SerialTimeoutException:
        print("Serial Timeout Error")

    except KeyboardInterrupt:
        print("Exiting Program")



#'CAN' Write Using PySerial
def writeOut(tx_data):
    mbed_serial.write(tx_data.encode())
    

while (True):
    data = readIn()
    print(f'THE RASPBERRY PI READ AS CAN THE FOLLOWING MESSAGE: {data}\n')
    print(f'SENDING CAN MESSAGE TO NUCLEO\n')
    writeOut(tx_data);
    # print(f'READING FROM NUCLEO: {readIn()}\n')
