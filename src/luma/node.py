import logging
import os
import signal
import socket
import subprocess
import threading
from typing import Optional

from rich.status import Status

logger = logging.getLogger(__name__)


def get_node_root(project_root: str) -> str:
    return os.path.join(project_root, ".luma")


def is_node_installed() -> bool:
    try:
        result = subprocess.run(
            ["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def install_node_modules(node_root: str):
    assert os.path.exists(node_root), f"Path '{node_root}' doesn't exist."

    package_json_path = os.path.join(node_root, "package.json")
    assert os.path.exists(
        package_json_path
    ), f"No 'package.json' found in '{node_root}'."

    try:
        with Status("[bold green]Installing dependencies..."):
            subprocess.run(
                ["npm", "install"],
                cwd=node_root,
                check=True,
                capture_output=True,
            )
        logger.info("Succesfully installed dependencies.")
    except subprocess.CalledProcessError:
        logger.error("Error occurred while installing node modules")
        raise


def run_node_dev(project_root: str, port: Optional[int]):
    node_root = get_node_root(project_root)

    if port is None:
        port = _find_free_port(start=3000)

    command = ["npm", "run", "dev", "--", "--port", f"{port}"]

    status = Status("Starting development server...")
    status.start()

    try:
        process = subprocess.Popen(
            command,
            cwd=node_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid,
        )

        def stream_output():
            ready_seen = False
            for line in process.stdout:
                if not ready_seen and "Ready in" in line:
                    ready_seen = True
                    status.stop()
                    logger.info(
                        f"Started development server at http://localhost:{port}"
                    )

        thread = threading.Thread(target=stream_output)
        thread.start()

        process.wait()

    except KeyboardInterrupt:
        os.killpg(os.getpgid(process.pid), signal.SIGINT)

    else:
        if process.returncode != 0:
            logger.error("Error occurred while running development server.")
            logger.error(process.stderr)

    # TODO: Clean up this logic. We're probably leaking some resources.
    finally:
        status.stop()
        process.wait()
        thread.join()
        logger.info("Development server stopped.")


def _find_free_port(*, start=3000):
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                logger.debug(f"Port {port} already in-use. Trying {port + 1}...")
                port += 1
