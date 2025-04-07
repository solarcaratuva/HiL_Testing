import git
from datetime import datetime
#import docker 
import subprocess
import os
import config


def gitPull(branch: str) -> tuple[bool, str]:
    try:
        repo = git.Repo(config.REPO_ROOT)
        origin = repo.remote(name='origin')
        origin.fetch()

        remote_branches = [ref.name.split('/')[-1] for ref in origin.refs]
        if branch not in remote_branches:
            return False, f"Branch \"{branch}\" does not exist!"
        repo.git.checkout(branch)
        origin.pull()

        lastCommit = repo.head.commit.committed_date
        time = datetime.fromtimestamp(lastCommit)
        time = time.strftime("%H:%M:%S %Y-%m-%d")
        return True, f"Last Commit at {time}"
    except Exception as e:
        return False, str(e)


def compile() -> bool:
    compileCmd = config.REPO_CONFIG["compileCmd"]
    containerName = config.REPO_CONFIG["containerName"]
    client = docker.from_env()
    container = client.containers.get(containerName)
    container.start()

    # compileCmd = "cd ./Rivanna2/ && ./compile.sh"
    exitCode, output = container.exec_run(f"sh -c '{compileCmd}'")
    logPath = os.path.join(config.LOG_FOLDER, "compile.log")
    with open(logPath, "w") as log:
        if output:
            log.write(output.decode())
        else:
            log.write("NO OUTPUT")
    return exitCode == 0


def upload(board: str) -> bool:
    uploadCmd = config.REPO_CONFIG["boards"][board]["uploadCmd"]
    command = f"cd {config.REPO_ROOT} && {uploadCmd}"
    logPath = os.path.join(config.LOG_FOLDER, f"upload_{board}.log")
    with open(logPath, "w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=log, encoding="utf-8", shell=True)
        process.wait()
    return process.returncode == 0
