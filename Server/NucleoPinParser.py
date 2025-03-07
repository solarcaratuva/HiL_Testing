import re
import os
import config

def parse_nucleo_pindef_pins(board: str) -> dict[str, str]:
    """Returns a dictionary mapping nice pin names (ex. THROTTLE_PEDAL) to actual pin names (ex. PC_10)"""

    pindef_path = os.path.join(config.REPO_ROOT, board, "include", "pindef.h")

    with(open(pindef_path, "r")) as pindef_file:
        pindef_content = pindef_file.read()

    # extract conditional block under #ifdef TARGET_NUCLEO_F413ZH
    conditional_block_pattern = r"#ifdef\s+TARGET_NUCLEO_F413ZH(.*?)#endif"
    conditional_content = re.search(conditional_block_pattern, pindef_content, re.DOTALL).group(1)

    # regex to find the define statements with pin names and numbers
    define_pattern = r"#define\s+(\w+)\s+([A-Z]+_[0-9]+)"
    pin_definitions = re.findall(define_pattern, conditional_content)

    # convert the pin defintions to a dictionary
    pin_dict = dict()
    for pin_name, pin_number in pin_definitions:
        pin_dict[pin_name] = pin_number

    return pin_dict


def parse_gpio_pins(board: str) -> dict[str, str]:
    """Returns a dictionary mapping nice pin names (ex. THROTTLE_PEDAL) to pin types (ex. AnalogIn)"""

    maincpp_path = os.path.join(config.REPO_ROOT, board, "src", "main.cpp")

    with(open(maincpp_path, "r")) as main_file:
        main_file_content = main_file.read()

    regex_pattern = r"(DigitalOut|DigitalIn|AnalogIn)\s+\w+\((\w+)[,\)]"
    pins = re.findall(regex_pattern, main_file_content)

    pin_dict = dict()
    for pin_type, pin_name in pins:
        pin_dict[pin_name] = pin_type

    return pin_dict