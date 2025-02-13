# CAN Message Definitions

CAN Messages for Rivanna3. Messages from Rivanna2 are under the Rivanna2 branch. 

## Software Installation

1. Clone this repo
2. Install cantools by running `py -m pip install cantools`
    - Note that you may need to use `python` or `python3` instead of `py`
3. Install [Kvaser Database Editor](https://www.kvaser.com/download/)
    - Version 3 recommended  

## Use
1. Use the *Kvaser Database Editor* to modify or create DBC files that define our CAN messages
2. To generate C CAN structs, run `cantools generate_c_source path`, replacing `path` with the path of the DBC file
3. To generate the 'wrapper' header files for each message type, run `py generate.py {DBC file path}`
4. Add a message ID entry to `Common/include/CANStructMessageIDs.h`