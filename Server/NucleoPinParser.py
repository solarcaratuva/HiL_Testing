import re
import os
import config

_PIN = re.compile(r"^[ \t]*#define[ \t]+(\w+)[ \t]+([A-Z]+_[0-9]+)", re.M)


def board_folder(board: str) -> str:
    """Rivanna3S config keys (TopDist) sit next to TopDistBoard. Rivanna3 uses the key as the folder."""
    root = config.REPO_ROOT
    named = os.path.join(root, board)
    if os.path.isfile(os.path.join(named, "Inc", "pindef.h")) or os.path.isfile(os.path.join(named, "include", "pindef.h")):
        return named
    sibling = os.path.join(root, board + "Board")
    if os.path.isdir(sibling):
        return sibling
    return named


def _pindef_text(folder: str) -> str:
    inc = os.path.join(folder, "Inc", "pindef.h")
    old = os.path.join(folder, "include", "pindef.h")
    path = inc if os.path.isfile(inc) else old
    with open(path) as pindef_file:
        text = pindef_file.read()
    if path == old:
        text = re.search(r"#ifdef\s+TARGET_NUCLEO_F413ZH(.*?)#endif", text, re.DOTALL).group(1)
        text = text.split("#else", 1)[0]
    return text


def parse_nucleo_pindef_pins(board: str) -> dict[str, str]:
    """Nice pin name (THROTTLE_WIPER) to port pin (PA_3)."""
    return dict(_PIN.findall(_pindef_text(board_folder(board))))


def parse_gpio_pins(board: str) -> dict[str, str]:
    """Nice pin name to DigitalOut / DigitalIn / AnalogIn."""
    folder = board_folder(board)
    path = os.path.join(folder, "Src", "main.cpp")
    if not os.path.isfile(path):
        path = os.path.join(folder, "src", "main.cpp")
    with open(path) as main_file:
        text = main_file.read()
    kinds = re.findall(r"(DigitalOut|DigitalIn|AnalogIn)\s+\w+\((\w+)[,\)]", text)
    return {name: kind for kind, name in kinds}
