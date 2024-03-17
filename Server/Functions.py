import git
from datetime import datetime
import docker 
import subprocess
from contextlib import redirect_stdout, redirect_stderr
import importlib
import importlib.util
import traceback
import os
import shutil

def getTests(name: str, testFolder: str) -> tuple[list, str]:
    if os.path.exists(f"{testFolder}{name}.txt"):
        with open(f"{testFolder}{name}.txt", "r") as file:
            tests = [n.replace("\n", "") for n in file.readlines()]
        for test in tests:
            if not os.path.exists(f"{testFolder}{test}.py"):
                return tests, f"\"{test}\" isn't a valid test"
        return tests, None
        
    elif os.path.exists(f"{testFolder}{name}.py"):
        return [name,], None
    else:
        return [name,], f"\"{name}\" isn't a valid test"

def gitPull(repoPath: str, branch: str) -> tuple[bool, str]:
    try:
        repo = git.Repo(repoPath)
        origin = repo.remote(name='origin')
        origin.pull()

        if branch not in repo.refs:
            return False, f"Branch \"{branch}\" does not exist!"
        repo.git.checkout(branch)

        lastCommit = repo.head.commit.committed_date
        time = datetime.fromtimestamp(lastCommit)
        time = time.strftime("%H:%M:%S %Y-%m-%d")
        return True, f"Last Commit at {time}"
    except Exception as e:
        return False, str(e)


def compile(repoName: str, logPath: str) -> bool:
    containerName = f"{repoName}_compile"
    client = docker.from_env()
    container = client.containers.get(containerName)
    container.start()

    command = "cd ./Rivanna2/ && ./compile.sh"
    exitCode, output = container.exec_run(f"sh -c '{command}'", demux=True)
    with open(logPath, "w") as log:
        if output[0] is not None:
            log.write(output[0].decode("utf-8"))
        if output[1] is not None:
            log.write(output[1].decode("utf-8"))
    return exitCode == 0


def upload(repoPath:str, uploadCmd: str, logPath:str) -> bool:
    command = f"cd {repoPath} && {uploadCmd}"
    with open(logPath, "w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=log, encoding="utf-8", shell=True)
        process.wait()
    return process.returncode == 0


def pipInstall(reqsPath: str, logPath: str) -> bool:
    command = f".\\.tenv\\Scripts\\activate && pip install -r {reqsPath}"
    with open(logPath, "w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=log, encoding="utf-8", shell=True)
        process.wait()
    return process.returncode == 0


def runTest(testName: str, testPath: str, logPath: str, config: dict) -> bool:
    try:
        spec = importlib.util.spec_from_file_location(testName, testPath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with open(logPath, "w") as log:
            with redirect_stdout(log):
                with redirect_stderr(log):
                    result = module.runTest(config)
            if type(result) is bool:
                return result
            else:
                log.write("ERROR: Test failed to return a boolean")
                return None
    except Exception as ex:
        with open(logPath, "a") as log:
            log.write("\n\nEXCEPTION THROWN\n\n")
            traceback.print_exception(type(ex), ex, ex.__traceback__, file=log)
        return None
    

def purgeOldLogs(daysAgo: int, logs_folder: str) -> None:
    currentTime = datetime.timestamp(datetime.now())
    for logs in os.listdir(logs_folder):
        creationTime = os.path.getctime(f"{logs_folder}\\{logs}")
        if (currentTime - creationTime) > 60*60*24*daysAgo:
            shutil.rmtree(f"{logs_folder}\\{logs}")
