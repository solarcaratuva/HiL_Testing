import os.path
import unittest
import argparse
import json
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
new_root = os.path.abspath(os.path.join(script_dir, "..", "Testing_Library"))
sys.path.append(new_root)

def make_suite(board_folder, config_data):
    # OLD VERSION (if you want only specific tests): 
    # embedded_tests = [ExampleTestStrings("test_add"), ExampleTestStrings("test_subtract")]

    # NEW VERSION (if you want all tests in the ExampleTestStrings.py file):
    loader = unittest.TestLoader()
    current_suite = unittest.TestSuite()

    try:
        discovered_tests = loader.discover(start_dir=board_folder, pattern="*.py")
        print("TESTS: ", discovered_tests)
    except Exception as e:
        print(f"Error discovering tests in {board_folder}: {e}")

    #print("Done with discovering tests: ", discovered_tests)
    #for test in discovered_tests:
    #    for test_case in test:
    #        for single_test in test_case:
    #            single_test.config_data = config_data  # Attach config_data to each test instance
    #        current_suite.addTest(test_case)

    return discovered_tests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run test suite with optional verbosity.")
    parser.add_argument(
        "-v", "--verbosity", 
        type=int, 
        choices=[0, 1, 2], 
        default=1,
        help="Set verbosity level (0, 1, or 2). Default is 1."
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    hil_config_filepath = os.path.join(script_dir, "hil_config.json")
    with(open(hil_config_filepath, "r")) as hil_config_file:
        hil_config = json.load(hil_config_file)
     
    rivanna_root_path = hil_config["rivanna_root"]
    board_names = hil_config["boards"]

    all_suites = unittest.TestSuite()

    for board in board_names:
        
        board_folder = os.path.join(rivanna_root_path, board, "tests/")
        print(f"Checking for tests at path: {board_folder}")
        
        if os.path.isdir(board_folder):
            suite = make_suite(board_folder, hil_config)
            all_suites.addTests(suite)
        else:
            print(f"Warning: Folder for board '{board}' not found at path: {board_folder}")

    runner = unittest.TextTestRunner(verbosity=args.verbosity)
    runner.run(all_suites)


