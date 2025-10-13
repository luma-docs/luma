import logging
import os
import tempfile
import time
import zipfile
from http import HTTPStatus
from typing import Optional

import keyring
import requests
import typer
from pathspec import PathSpec

POLLING_TIMEOUT_SECONDS = 15 * 60
POLLING_INTERVAL_SECONDS = 10

LUMA_API_KEY_ENV_VAR = "LUMA_API_KEY"

logger = logging.getLogger(__name__)


def _get_api_key():
    """Get the Luma API key.

    If the API key isn't stored as an environment variable, this function trys to get
    it from the system's keyring. If the key isn't found, the CLI prompt the user for
    the API key and save to the system's keyring.
    """
    if LUMA_API_KEY_ENV_VAR in os.environ:
        return os.environ[LUMA_API_KEY_ENV_VAR]

    api_key = keyring.get_password("luma", "api_key")

    if not api_key:
        api_key = typer.prompt("Enter API key", hide_input=True)
        keyring.set_password("luma", "api_key", api_key)

    return api_key


def _load_ignore_spec(node_root: str) -> PathSpec:
    """
    Load the `.deployignore` located at the node root of the Luma project for
    ignoring files when zipping the project for deployment.

    Args:
        node_root: The node root of the current Luma project

    Returns:
        A PathSpec object created from the Luma project's `.deployignore`
    """
    ignore_path = os.path.join(node_root, ".deployignore")

    if not os.path.exists(ignore_path):
        logger.error("Missing .deployignore in node root.")
        raise typer.Exit(1)

    with open(ignore_path, "r") as file:
        return PathSpec.from_lines("gitwildmatch", file)


def build_project(node_root: str) -> str:
    """
    Zip all files in the node root to a temp file, skipping any files
    specified in the `.gitignore`.

    Args:
        node_root: The node root of the current Luma project

    Returns:
        The path to the tempfile containing the zipped Luma project
    """
    logger.info("Building project...")
    ignore_spec = _load_ignore_spec(node_root)
    temp_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)

    try:
        with zipfile.ZipFile(temp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(node_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, node_root)

                    if not ignore_spec.match_file(rel_path):
                        zipf.write(file_path, rel_path)

        return temp_zip.name
    except Exception as e:
        logger.error(f"Error building project: {e}")
        temp_zip.close()
        os.unlink(temp_zip.name)

        raise typer.Exit(1)


def deploy_project(build_path: str, package_name: str, version: Optional[str]):
    """
    Deploy the current project to luma-docs.org.

    Args:
        build_path: The path to the temporary build file
        package_name: The name of the package being deployed

    Returns:
        The string ID corresponding to the submitted deployment, used for
        monitoring deployment status.
    """
    logger.info("Queueing deployment...")

    if not os.path.exists(build_path):
        logger.error("Build file not found.")
        raise typer.Exit(1)

    api_url = f"https://yron03hrwk.execute-api.us-east-1.amazonaws.com/dev/packages/{package_name}"
    if version:
        api_url += f"/versions/{version}"

    api_key = _get_api_key()

    response = requests.get(api_url, headers={"x-api-key": api_key})

    presigned_url_data = response.json()

    with open(build_path, "rb") as file:
        response = requests.post(
            presigned_url_data["url"],
            headers={"x-api-key": api_key},
            data=presigned_url_data["fields"],
            files={"file": file},
        )

    if response.status_code != HTTPStatus.NO_CONTENT:
        logger.error(f"Deployment failed: {response.status_code} {response.text}")
        raise typer.Exit(1)


def monitor_deployment(package_name: str):
    """
    Monitor the status of the given deployment for up to `POLLING_TIMEOUT_SECONDS`. Checks
    the completion status of the deployment and will continue to poll every
    `POLLING_INTERVAL_SECONDS` until complete.

    Args:
        deployment_id: The id of the deployment to monitor
        package_name: The name of the package being deployed
    """
    logger.info("Monitoring deployment...")
    timeout = time.time() + POLLING_TIMEOUT_SECONDS

    while time.time() < timeout:
        if has_deployment_finished(package_name):
            return

        time.sleep(POLLING_INTERVAL_SECONDS)

    logger.warn("Timed out while monitoring deployment.")


def has_deployment_finished(package_name: str) -> bool:
    """
    Check if the deployment for the given package name has finished.

    Args:
        package_name: The name of the package being deployed

    Returns:
        True if the deployment is ready or has errored, false if the deployment
        is still in progress
    """
    try:
        response = requests.get(
            f"https://yron03hrwk.execute-api.us-east-1.amazonaws.com/status/packages/{package_name}/deployments",
            headers={"x-api-key": _get_api_key()},
        )

        body = response.json()
        status = body["status"]

        if status == "READY":
            logger.info(f"Deployment successful! https://{package_name}.luma-docs.org")
        elif status == "ERROR":
            logger.error(f"Deployment failed: {body['errorMessage']}")
            raise typer.Exit(1)
        elif status == "CANCELED":
            logger.warn(f"Deployment canceled: {body['errorMessage']}")
            raise typer.Exit(1)
        else:
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while checking deployment status: {e}")
        return False

    return True


def cleanup_build(build_path: str):
    """
    Clean up the Luma build by removing the temporary zip file located at `build_path`.

    Args
        build_path: The temporary file location of the zipped Luma project
    """
    if os.path.exists(build_path):
        os.unlink(build_path)
