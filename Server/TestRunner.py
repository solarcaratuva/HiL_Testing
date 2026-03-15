import os
import unittest
import sys
import config
import xmlrunner

# Adds the Testing_Library to the path, allowing tests to import from it
script_dir = os.path.dirname(os.path.abspath(__file__))
new_root = os.path.abspath(os.path.join(script_dir, "..", "Testing_Library"))
sys.path.append(new_root)
sys.path.append(os.getcwd())

from upload_wrapper import upload_firmware

# Custom TestSuite that overrides the run method to run setup and teardown code; added code to maek firmware upload once per board, not test
class CustomTestSuite(unittest.TestSuite):
    def __init__(self, tests, board_name):
        super().__init__(tests)
        self.board_name = board_name

    def run(self, result, debug=False):
        setup_suite(self.board_name)
        super().run(result, debug)
        # teardown_suite(self.board_name) # optional

def setup_suite(board_name):
    print(f"[SUITE] Uploading firmware for {board_name}")
    upload_firmware(board_name)


def teardown_suite():
    print("Tearing down suite...") # replace with teardown code
    
def make_suite(board_folder):
    loader = unittest.TestLoader()

    try:
        discovered_tests = loader.discover(start_dir=board_folder, pattern="*.py")
        print("TESTS: ", discovered_tests)
    except Exception as e:
        print(f"Error discovering tests in {board_folder}: {e}")

    return discovered_tests

def run_tests() -> None:

    # monitor script
    import subprocess, datetime

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("logs", exist_ok=True)
    serial_log = os.path.abspath(f"logs/{ts}_serial.txt")

    monitor_proc = subprocess.Popen([sys.executable, "monitor.py", "--log", serial_log])
    print(f"[ARTIFACT] serial_log={serial_log}")

    board_names = config.REPO_CONFIG["boards"].keys()
    print("DEBUG: Boards in config:", board_names)


    all_suites = unittest.TestSuite()

    for board in board_names:
        board_folder = os.path.join(config.REPO_ROOT, board, "tests/")
        print(f"Checking for tests at path: {board_folder}")
        
        if os.path.isdir(board_folder):
            suite = make_suite(board_folder)
            custom_suite = CustomTestSuite([suite], board)
            all_suites.addTest(custom_suite)
            print("Added test to custom suite")
        else:
            print(f"Warning: Folder for board '{board}' not found at path: {board_folder}")

    try:
        with open("test-results.xml", "wb") as output:
            runner = xmlrunner.XMLTestRunner(output=output, buffer=True)
            runner.run(all_suites)
    finally:
        monitor_proc.terminate()
        try:
            monitor_proc.wait(timeout=2)
        except Exception:
            monitor_proc.kill()

