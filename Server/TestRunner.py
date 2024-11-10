import os
import unittest
import argparse
import json

def make_suite(board_folder):
    # OLD VERSION (if you want only specific tests): 
    # embedded_tests = [ExampleTestStrings("test_add"), ExampleTestStrings("test_subtract")]

    # NEW VERSION (if you want all tests in the ExampleTestStrings.py file):
    loader = unittest.TestLoader()
    current_suite = unittest.TestSuite()

    current_suite.addTests(loader.discover(start_dir=board_folder, pattern="*.py"))
    return current_suite

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

    hil_config_filepath = "hil_config.json"
    with(open(hil_config_filepath, "r")) as hil_config_file:
        hil_config = json.load(hil_config_file)
     
    rivanna_root_path = hil_config["rivanna_root"]
    board_names = hil_config["boards"]

    all_suites = unittest.TestSuite()

    for board in board_names:
        board_folder = os.path.join(rivanna_root_path, board, "tests/")
        print(f"Checking for tests at path: {board_folder}")
        
        if os.path.isdir(board_folder):
            suite = make_suite(board_folder)
            all_suites.addTests(suite)
        else:
            print(f"Warning: Folder for board '{board}' not found at path: {board_folder}")

    runner = unittest.TextTestRunner(verbosity=args.verbosity)
    runner.run(all_suites)


