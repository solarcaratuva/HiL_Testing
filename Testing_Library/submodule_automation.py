import git
from datetime import datetime
import subprocess
import os
import sys
import json
import requests

# Make sure we can import Server/config.py
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Server"))
from Server import config


def get_repo_root_from_config(repo_name: str) -> str:
    """
    Reads server_config.json via config.py to get the repo root
    without calling read_in_configs() (avoids hil_config.json dependency).
    """
    server_config_path = os.path.join(os.path.dirname(config.__file__), "server_config.json")
    with open(server_config_path, "r") as f:
        server_config = json.load(f)

    if repo_name not in server_config.get("repo_paths", {}):
        raise ValueError(f"Unknown repo name '{repo_name}' in server_config.json")

    return server_config["repo_paths"][repo_name]


def ensure_submodule_initialized(path: str, repo_root: str):
    """Ensure the given submodule is initialized and updated."""
    try:
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive", "--", path],
            cwd=repo_root,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to initialize submodule at {path}: {e}")


def gitPull(branch: str, repo_root: str, path: str = None, is_submodule: bool = False) -> tuple[bool, str]:
    """Pulls the given branch for the repo or submodule."""
    try:
        repo_path = os.path.join(repo_root, path) if path else repo_root
        repo_path = os.path.abspath(repo_path)

        if is_submodule:
            ensure_submodule_initialized(path, repo_root)

        repo = git.Repo(repo_path)

        origin = repo.remote(name="origin")
        origin.fetch()

        remote_branches = [ref.name.split("/")[-1] for ref in origin.refs]
        if branch not in remote_branches:
            return False, f"[GIT ERROR] Branch \"{branch}\" does not exist remotely in {path or 'main repo'}!"

        repo.git.checkout(branch)
        origin.pull()

        last_commit = repo.head.commit.committed_date
        time = datetime.fromtimestamp(last_commit).strftime("%H:%M:%S %Y-%m-%d")
        return True, f"Checked out '{repo.active_branch.name}' in {path or 'main repo'}. Last commit at {time}"

    except Exception as e:
        return False, f"[GIT ERROR] {str(e)}"
