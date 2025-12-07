import os
import json
import NucleoPinParser


SERVER_CONFIG = dict()
REPO_ROOT = str()
REPO_CONFIG = dict()

PIN_NAMES_MAP = dict()
PIN_TYPES_MAP = dict()

LOG_FOLDER = os.path.join(os.path.dirname(__file__), "..", "logs")


def read_in_configs(repoName: str) -> bool:
    """Reads in server and repo config files for a given repo. Sets global constants. Returns True if `repoName` is a valid repo, False otherwise."""
    global SERVER_CONFIG, REPO_CONFIG, REPO_ROOT

    server_config_path = os.path.join(os.path.dirname(__file__), "server_config.json")
    with open(server_config_path, 'r') as file:
        SERVER_CONFIG = json.load(file)

    if repoName not in SERVER_CONFIG["repo_paths"]:
        return False
    REPO_ROOT = SERVER_CONFIG["repo_paths"][repoName]
    
    repo_config_path = os.path.join(REPO_ROOT, "hil_config.json")
    print(f"[DEBUG] Reading hil_config.json from: {repo_config_path}")
    with open(repo_config_path, 'r') as file:
        REPO_CONFIG = json.load(file)

    return True

def read_in_nucleo_pinmaps(board: str) -> None:
    """Parses pin data for a given board in a given repo. Sets global constants. Must have called `read_in_configs()` already."""
    global PIN_NAMES_MAP, PIN_TYPES_MAP

    PIN_NAMES_MAP = NucleoPinParser.parse_nucleo_pindef_pins(board)
    PIN_TYPES_MAP = NucleoPinParser.parse_gpio_pins(board)
