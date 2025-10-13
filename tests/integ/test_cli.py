import os
import signal
import socket
import subprocess
import time

import pytest
import requests
import requests.exceptions
import yaml
from typer.testing import CliRunner

from luma.main import app

runner = CliRunner()


@pytest.fixture
def tmp_cwd(tmp_path):
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)


@pytest.fixture
def unused_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # Bind to any available address and port 0
        return str(s.getsockname()[1])  # Get the assigned port number


def run_dev(port: int):
    # We can't define this function in a test because it needs to be run in a separate
    # process, and 'multiprocessing' can't pickle nested functions.
    result = runner.invoke(app, ["dev", "--port", str(port)])
    assert result.exit_code == 0, result.stdout


def test_init_and_dev(tmp_cwd, unused_port):
    # Create a new project.
    result = runner.invoke(app, ["init"], input="math\n")
    assert result.exit_code == 0, result.stdout
    assert os.path.exists("docs/")
    assert os.path.exists("docs/luma.yaml")
    assert os.path.exists("docs/.luma/")

    with open("docs/luma.yaml") as file:
        config = yaml.safe_load(file)
    assert config["name"] == "math"

    # Switch to the project directory.
    os.chdir("docs/")

    try:
        process = subprocess.Popen(["luma", "dev", "--port", unused_port])

        time_elapsed = 0
        while time_elapsed < 30:
            try:
                response = requests.get(f"http://localhost:{unused_port}")
                break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
                time_elapsed += 1

        assert response.status_code == 200, response.status_code

    # Cleanup.
    finally:
        os.kill(process.pid, signal.SIGINT)
        process.wait()
