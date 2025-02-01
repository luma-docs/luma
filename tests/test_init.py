import multiprocessing
import os
import signal
import socket
import time

import pytest
import requests
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


def test_init(tmp_cwd):
    result = runner.invoke(app, ["init"], input="math\n")

    assert result.exit_code == 0, result.stdout
    assert os.path.exists("docs/")
    assert os.path.exists("docs/luma.yaml")
    assert os.path.exists("docs/.luma/")

    with open("docs/luma.yaml") as file:
        config = yaml.safe_load(file)

    assert config["name"] == "math"


def run_dev(port: int):
    # We can't define this function in a test because it needs to be run in a separate
    # process, and 'multiprocessing' can't pickle nested functions.
    result = runner.invoke(app, ["dev", "--port", str(port)])
    assert result.exit_code == 0, result.stdout


def test_dev(tmp_cwd, unused_port):
    runner.invoke(app, ["init"], input="math\n")
    os.chdir("docs/")

    process = multiprocessing.Process(target=run_dev, args=(unused_port,), daemon=True)
    process.start()
    time.sleep(3)

    response = requests.get(f"http://localhost:{unused_port}")
    assert response.status_code == 404
    response = requests.get(f"http://localhost:{unused_port}/getting-started")
    assert response.status_code == 200

    os.kill(process.pid, signal.SIGINT)
    process.join()
