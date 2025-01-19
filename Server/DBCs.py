# The point of this file is to create DBCs once, instead of repeatedly being recreated whenever DbConnection is called
import cantools as ct
import os

# DBC_FILES are the 'definitions'/'mappings' files, they are not parseable yet.
dbc_files = os.listdir("/home/solarcar/CAN-messages")
DBCs = [ct.db.load_file(f"/home/solarcar/CAN-messages{file}") for file in dbc_files if file.endswith(".dbc")]
# DBCs takes the files from DBC_FILES and turns each file into a DBC Object that has functions to access can msg types
# Function in our code depend on these definitions/configurations to get information on each type of can message.

