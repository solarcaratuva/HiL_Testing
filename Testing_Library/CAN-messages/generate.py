import cantools as ct
import sys
import os


def camelcase_to_snakecase(camelcase: str) -> str:
    chars = list(camelcase)
    for i, char in enumerate(chars):
        if char.isupper() and i != 0:
            chars[i] = f"_{char}"
    return "".join(chars).lower()


def make_header_file_text(db_name: str, message_name_camelcase: str, signals: list[str]) -> str:
    message_name_snakecase = camelcase_to_snakecase(message_name_camelcase)
    signals_formatted_string = ", ".join([f"{signal} %u" for signal in signals])
    signals_variable_string = ", ".join(signals)
    

    return f"""
    #ifndef {message_name_snakecase}_CAN_Struct
    #define {message_name_snakecase}_CAN_Struct

    #include "CANStruct.h"
    #include "dbc/structs/{db_name}.h"
    #include "log.h"

    typedef struct {message_name_camelcase} : CANStruct, {db_name}_{message_name_snakecase}_t {{
        void serialize(CANMessage *message) {{
            {db_name}_{message_name_snakecase}_pack(message->data, this,
                {db_name.upper()}_{message_name_snakecase.upper()}_LENGTH);
            message->len = {db_name.upper()}_{message_name_snakecase.upper()}_LENGTH;
        }}

        void deserialize(CANMessage *message) {{
            {db_name}_{message_name_snakecase}_unpack(this, message->data,
                {db_name.upper()}_{message_name_snakecase.upper()}_LENGTH);
        }}

        uint32_t get_message_ID() {{ return {db_name.upper()}_{message_name_snakecase.upper()}_FRAME_ID; }}

        void log(int level) {{
            log_at_level(
                level,
                "{message_name_camelcase}: {signals_formatted_string}",
                {signals_variable_string});
        }}
    }} {message_name_camelcase};

    #endif
    """

def main() -> None:
    if len(sys.argv) != 2:
        print("ERROR: Must provide a .dbc file as an argument")
        return
    path = sys.argv[1]
    if not path.endswith(".dbc"):
        print("ERROR: Must be a .dbc file")
        return
    
    db = ct.db.load_file(path)
    db_name = os.path.splitext(os.path.basename(path))[0].lower()

    for messageType in db.messages:
        messageName = messageType.name
        signals = [signal.name for signal in messageType.signals]

        headerText = make_header_file_text(db_name, messageName, signals)

        with open(f"{messageName}CANStruct.h", "w") as file:
            file.write(headerText)

    print("Done")



if __name__ == "__main__":
    main()