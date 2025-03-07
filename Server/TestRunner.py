import os.path
import unittest
import json
import sys
import config

# Adds the Testing_Library to the path, allowing tests to import from it
script_dir = os.path.dirname(os.path.abspath(__file__))
new_root = os.path.abspath(os.path.join(script_dir, "..", "Testing_Library"))
sys.path.append(new_root)

def make_suite(board_folder):
    loader = unittest.TestLoader()

    try:
        discovered_tests = loader.discover(start_dir=board_folder, pattern="*.py")
        print("TESTS: ", discovered_tests)
    except Exception as e:
        print(f"Error discovering tests in {board_folder}: {e}")

    return discovered_tests

def run_tests() -> None:
    board_names = config.REPO_CONFIG["boards"]

    all_suites = unittest.TestSuite()

    for board in board_names:
        board_folder = os.path.join(config.REPO_ROOT, board, "tests/")
        print(f"Checking for tests at path: {board_folder}")
        
        if os.path.isdir(board_folder):
            suite = make_suite(board_folder)
            all_suites.addTests(suite)
        else:
            print(f"Warning: Folder for board '{board}' not found at path: {board_folder}")

    runner = unittest.TextTestRunner()
    runner.run(all_suites)
