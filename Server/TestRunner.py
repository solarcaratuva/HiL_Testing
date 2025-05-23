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

# Custom TestSuite that overrides the run method to run setup and teardown code
class CustomTestSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        setup_suite()
        super().run(result, debug)
        teardown_suite()

def setup_suite():
    print("Setting up suite...") # replace with setup code

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
    board_names = config.REPO_CONFIG["boards"].keys()

    all_suites = unittest.TestSuite()

    for board in board_names:
        board_folder = os.path.join(config.REPO_ROOT, board, "tests/")
        print(f"Checking for tests at path: {board_folder}")
        
        if os.path.isdir(board_folder):
            suite = make_suite(board_folder)
            custom_suite = CustomTestSuite([suite])
            all_suites.addTests(custom_suite)
        else:
            print(f"Warning: Folder for board '{board}' not found at path: {board_folder}")

    with open("test-results.xml", "wb") as output:
        runner = xmlrunner.XMLTestRunner(output=output, buffer=True)
        runner.run(all_suites)
