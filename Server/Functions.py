import git
from datetime import datetime
import docker 
import subprocess
import os
import config


def gitPull(repoPath: str, branch: str) -> tuple[bool, str]:
    try:
        repo = git.Repo(repoPath)
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


def compile(compileCmd: str, containerName: str) -> bool:
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


def upload(uploadCmd: str, board: str, repoPath: str) -> bool:
    command = f"cd {repoPath} && {uploadCmd}"
    logPath = os.path.join(config.LOG_FOLDER, f"upload_{board}.log")
    with open(logPath, "w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=log, encoding="utf-8", shell=True)
        process.wait()
    return process.returncode == 0
