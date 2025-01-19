import os
import json
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
hil_config_filepath = os.path.join(script_dir, "hil_config.json")
with(open(hil_config_filepath, "r")) as hil_config_file:
    hil_config = json.load(hil_config_file)

rivanna3_root_path = hil_config["rivanna3_root"]
base_path = os.path.expanduser("~")
pin_def = os.path.join(base_path, rivanna3_root_path.lstrip("/"), "PowerBoard/include/pindef.h")

with(open(pin_def, "r")) as pindef_file:
    pindef_content = pindef_file.read()

# extract conditional block under #ifdef TARGET_NUCLEO_F413ZH
conditional_block_pattern = r"#ifdef\s+TARGET_NUCLEO_F413ZH(.*?)#endif"
conditional_content = re.search(conditional_block_pattern, pindef_content, re.DOTALL).group(1)

# regex to find the define statements with pin names and numbers
define_pattern = r"#define\s+(\w+)\s+([A-Z]+_[0-9]+)"
pin_definitions = re.findall(define_pattern, conditional_content)

# convert the pin defintions to a dictionary
pin_dict = {}
for pin_name, pin_number in pin_definitions:
    pin_dict[pin_name] = pin_number

print("Extracted Pin Definitions:")
for pin_name, pin_number in pin_dict.items():
    print(f"{pin_name}: {pin_number}")