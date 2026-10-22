#!/usr/bin/env python3
"""Server reads each checkout's config, then compiles and flashes before the suite."""

import io
import json
import os
import sys
import tempfile
import textwrap
import types
import unittest
from pathlib import Path

docker = types.ModuleType("docker")
sys.modules["docker"] = docker
sys.modules["git"] = types.ModuleType("git")

xmlrunner = types.ModuleType("xmlrunner")


class XMLTestRunner:
    def __init__(self, output=None, buffer=True):
        pass

    def run(self, suite):
        return unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)


xmlrunner.XMLTestRunner = XMLTestRunner
sys.modules["xmlrunner"] = xmlrunner

SERVER = Path(__file__).resolve().parent
sys.path.insert(0, str(SERVER))
sys.path.insert(0, str(SERVER.parent / "Testing_Library"))

import config
import Functions
import TestRunner
import main
import upload_wrapper


class _Container:
    result = (0, b"built")

    def start(self):
        pass

    def exec_run(self, cmd):
        return self.result


_container = _Container()


class _Containers:
    def get(self, name):
        assert name == "Rivanna3S_compile"
        return _container


class _Client:
    containers = _Containers()


def _docker_ok():
    docker.from_env = lambda: _Client()


def _use_repo(root: Path):
    config.REPO_ROOT = str(root)
    config.LOG_FOLDER = str(root / "logs")
    os.makedirs(config.LOG_FOLDER, exist_ok=True)
    config.REPO_CONFIG = {
        "containerName": "Rivanna3S_compile",
        "compileCmd": "cmake --build build",
        "boards": {
            "TopDist": {"uploadCmd": "python3 -c \"import sys; print('flash failed'); sys.exit(1)\""},
            "BottomDist": {"uploadCmd": "python3 -c \"print('flashed')\""},
            "MotorBoard": {"uploadCmd": "python3 -c \"print('flashed')\""},
        },
    }


def _case(folder: Path, marker: Path):
    folder.mkdir(parents=True)
    folder.joinpath("test_board.py").write_text(textwrap.dedent(f"""
        import unittest
        class Case(unittest.TestCase):
            def test_runs(self):
                open({str(marker)!r}, "w").write("ran")
    """))


def test_server_config_names_both_checkouts():
    cfg = json.loads((SERVER / "server_config.json").read_text())
    assert "Rivanna3s" in cfg["repo_paths"]
    assert "Rivanna3" in cfg["repo_paths"]
    assert "Rivanna3S" not in cfg["repo_paths"]["Rivanna3"]


def test_each_run_reads_its_own_checkout():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        r3 = root / "Rivanna3"
        r3s = root / "Rivanna3S"
        r3.mkdir()
        r3s.mkdir()
        (r3 / "hil_config.json").write_text(json.dumps({
            "boards": {"PowerBoard": {"uploadCmd": "echo hi"}},
        }))
        (r3s / "hil_config.json").write_text(json.dumps({
            "containerName": "Rivanna3S_compile",
            "compileCmd": "cmake --build build",
            "boards": {
                "TopDist": {"uploadCmd": "python3 upload.py TopDist --hil"},
                "BottomDist": {"uploadCmd": "python3 upload.py BottomDist --hil"},
                "MotorBoard": {"uploadCmd": "python3 upload.py MotorBoard --hil"},
            },
        }))
        server_cfg = root / "server_config.json"
        server_cfg.write_text(json.dumps({"repo_paths": {
            "Rivanna3": str(r3),
            "Rivanna3s": str(r3s),
        }}))
        assert config.read_in_configs("Rivanna3s", server_config_path=str(server_cfg))
        assert config.REPO_ROOT == str(r3s)
        assert set(config.REPO_CONFIG["boards"]) == {"TopDist", "BottomDist", "MotorBoard"}
        assert config.REPO_CONFIG["containerName"] == "Rivanna3S_compile"
        assert config.read_in_configs("Rivanna3", server_config_path=str(server_cfg))
        assert config.REPO_ROOT == str(r3)
        assert set(config.REPO_CONFIG["boards"]) == {"PowerBoard"}
        assert config.REPO_CONFIG["boards"]["PowerBoard"]["uploadCmd"] == "echo hi"


def test_failed_compile_is_logged_and_skips_upload():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _use_repo(root)
        _container.result = (1, b"cmake failed")
        _docker_ok()
        popped = []
        real_popen = Functions.subprocess.Popen

        def spy(*args, **kwargs):
            popped.append(args[0] if args else kwargs)
            return real_popen(*args, **kwargs)

        Functions.subprocess.Popen = spy
        old = os.getcwd()
        os.chdir(root)
        try:
            assert TestRunner.run_tests() is False
        finally:
            Functions.subprocess.Popen = real_popen
            os.chdir(old)
        assert "cmake failed" in (root / "logs" / "compile.log").read_text()
        assert popped == []


def test_missing_container_is_logged():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _use_repo(root)

        def boom():
            raise RuntimeError("no such container")

        docker.from_env = boom
        assert Functions.compile() is False
        assert "no such container" in (root / "logs" / "compile.log").read_text()


def test_failed_upload_is_logged_and_fails_that_suite():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _use_repo(root)
        _container.result = (0, b"built")
        _docker_ok()
        top = root / "top_ran"
        bot = root / "bot_ran"
        _case(root / "TopDist" / "tests", top)
        _case(root / "BottomDist" / "tests", bot)
        old = os.getcwd()
        os.chdir(root)
        try:
            assert TestRunner.run_tests() is False
        finally:
            os.chdir(old)
        assert "flash failed" in (root / "logs" / "upload_TopDist.log").read_text()
        assert not top.exists()
        assert bot.exists()
        assert "flashed" in (root / "logs" / "upload_BottomDist.log").read_text()


def test_upload_helper_calls_rivanna3s_with_hil_flag():
    seen = []

    def fake_run(cmd, check):
        seen.append(cmd)

    real = upload_wrapper.subprocess.run
    upload_wrapper.subprocess.run = fake_run
    try:
        upload_wrapper.upload_firmware("MotorBoard")
    finally:
        upload_wrapper.subprocess.run = real
    cmd = seen[0]
    assert cmd[1].endswith("/Rivanna3S/upload.py")
    assert cmd[2:] == ["motor", "--hil"]


def test_main_stops_when_compile_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _use_repo(root)
        _container.result = (1, b"cmake failed")
        _docker_ok()

        def fake_read(name, server_config_path=None):
            assert name == "Rivanna3s"
            return True

        real = config.read_in_configs
        config.read_in_configs = fake_read
        try:
            try:
                main.main()
            except SystemExit as e:
                assert e.code == 1
            else:
                raise AssertionError("compile failure should stop the run")
        finally:
            config.read_in_configs = real
        assert "cmake failed" in (root / "logs" / "compile.log").read_text()


if __name__ == "__main__":
    test_server_config_names_both_checkouts()
    test_each_run_reads_its_own_checkout()
    test_failed_compile_is_logged_and_skips_upload()
    test_missing_container_is_logged()
    test_failed_upload_is_logged_and_fails_that_suite()
    test_upload_helper_calls_rivanna3s_with_hil_flag()
    test_main_stops_when_compile_fails()
    print("ok")
