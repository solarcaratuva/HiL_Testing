import os
import sys
import json
from datetime import datetime
import shutil
from Functions import *

def main() -> None:
    # Read in config.json, read in CLI args (repo name, branch, test), validate input
    if len(sys.argv) < 4:
        print("Input Validation Error: 3 CLI args demanded")
        return

    baseFolder = os.path.dirname(os.path.abspath(__file__))
    with open(f"{baseFolder}/config.json", "r") as file:
        CONFIG = json.load(file)
    REPOS_FOLDER = CONFIG["repos_folder"]
    TESTS_FOLDER = CONFIG["tests_folder"]
    LOGS_FOLDER = CONFIG["logs_folder"]
    BOARDS = CONFIG["boards"]

    repo_name = sys.argv[1]
    repos = os.listdir(REPOS_FOLDER)
    if repo_name not in repos:
        print(f"Input Validation Error: Repo \"{repo_name}\" is invalid. Valid repos are: {', '.join(repos)}")
        return

    branch = sys.argv[2]

    flags = set(sys.argv[4:]) if len(sys.argv) >= 4 else set()

    time = datetime.now()
    timestamp = f"{time.strftime('%Y-%m-%d')}_{time.strftime('%H-%M-%S')}"
    this_logs_folder = f"{LOGS_FOLDER}log_{timestamp}/"
    os.mkdir(this_logs_folder)
    
    # Pull the selected repo (to get new changes)
    if "--skip-git" not in flags:
        success, text = gitPull(REPOS_FOLDER + repo_name, branch)
        if success:
            print(f"Git Success: {text}")
        else:
            print(f"Git Error: {text}")
            if "--force-run" not in flags:
                return

    # Test(s) input validation
    testFolderPath = f"{REPOS_FOLDER}{repo_name}\\{TESTS_FOLDER}"
    tests, error = getTests(sys.argv[3], testFolderPath)
    if error:
        print(f"Input Validation Error: {error}")
        if "--force-run" not in flags:
            return

    # Compile the repo in docker on the Pi
    if "--skip-compile" not in flags:
        success = compile(repo_name, this_logs_folder + "compile.txt")
        if success:
            print("Compile Success")
        else:
            print("Compile Error, see the log")
            if "--force-run" not in flags:
                return
    
    # Upload the code to the boards
    for board in BOARDS:
        if "--skip-upload" in flags or f"--skip-upload-{board}" in flags:
            continue
        logPath = f"{this_logs_folder}upload_{board}.txt"
        success = upload(REPOS_FOLDER + repo_name, board["upload_script"], logPath)
        if success:
            print(f"Upload {board} Success")
        else:
            print(f"Upload {board} Error, see the log")
            if "--force-run" not in flags:
                return
        
    # pip install dependencies for premade tests
    if "--skip-pip" not in flags:
        reqsPath = f"{REPOS_FOLDER}{repo_name}/{TESTS_FOLDER}requirements.txt"
        success = pipInstall(reqsPath, this_logs_folder + "pip.txt")
        if success:
            print("Pip Success")
        else:
            print("Pip Error, see the log")
            if "--force-run" not in flags:
                return

    # Run premade test(s) and save output to a log file
    successes, failures = 0, 0
    for i in range(len(tests)):
        test = tests[i]
        if "--skip-tests" in flags or f"--skip-test-{test}" in flags:
            continue
        testPath = f"{testFolderPath}{test}.py"
        logPath = f"{this_logs_folder}test_{test}.txt"
        success = runTest(test, testPath, logPath, CONFIG)

        count = f"[{i+1}/{len(tests)}]\t" if len(tests) > 1 else ""
        text = None
        if success is True:
            text = "\033[92m Success \033[0m"
            successes += 1
        elif success is False:
            text = "\033[91m Failure \033[0m"
            failures += 1
        elif success is None:
            text = "\033[93m Exception \033[0m"
        print(f"{count}{text}\t{test}")
    if len(tests) > 1:
        print(f"Summary: {successes} successes, and {failures} failures")
    shutil.rmtree(f"{testFolderPath}__pycache__")

    # remove very old log files
    if "--skip-purge" not in flags:
        purgeOldLogs(0.5, LOGS_FOLDER)


    print(f"Done! Logs saved to {this_logs_folder}")





if __name__ == "__main__":
    main()
