import logging
import os
import tempfile
import time
import zipfile

import keyring
import requests
import typer
from pathspec import PathSpec

POLLING_TIMEOUT_SECONDS = 15 * 60
POLLING_INTERVAL_SECONDS = 10

logger = logging.getLogger(__name__)


def _get_api_key():
    """
    Get the Luma API key from the system's keyring. If the key isn't found, the CLI
    will prompt for the API key and save to the system's keyring.
    """
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
        node_root (str): The node root of the current Luma project

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
        node_root (str): The node root of the current Luma project

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


def deploy_project(build_path: str, package_name: str) -> str:
    """
    Deploy the current project to luma-docs.org.

    Args:
        build_path (str): The path to the temporary build file
        package_name (str): The name of the package being deployed

    Returns:
        The string ID corresponding to the submitted deployment, used for
        monitoring deployment status.
    """
    logger.info("Queueing deployment...")

    if not os.path.exists(build_path):
        logger.error("Build file not found.")
        raise typer.Exit(1)

    with open(build_path, "rb") as file:
        response = requests.post(
            f"https://yron03hrwk.execute-api.us-east-1.amazonaws.com/dev/packages/{package_name}",
            headers={"x-api-key": _get_api_key(), "Content-Type": "application/zip"},
            data=file,
        )

    if response.status_code == 202:
        body = response.json()
        return body["deploymentId"]
    else:
        logger.error(f"Deployment failed: {response.status_code} {response.text}")
        raise typer.Exit(1)


def monitor_deployment(deployment_id: str, package_name: str):
    """
    Monitor the status of the given deployment for up to `POLLING_TIMEOUT_SECONDS`. Checks
    the status returned from the Luma API for one of `READY|ERROR|CANCELED` to log, and will
    continue to poll every `POLLING_INTERVAL_SECONDS` if the status is still `QUEUED`.

    Args:
        deployment_id (str): The id of the deployment to monitor
        package_name (str): The name of the package being deployed
    """
    logger.info("Monitoring deployment...")
    timeout = time.time() + POLLING_TIMEOUT_SECONDS

    while time.time() < timeout:
        try:
            response = requests.get(
                f"https://yron03hrwk.execute-api.us-east-1.amazonaws.com/status/packages/{package_name}/deployments/{deployment_id}",
                headers={"x-api-key": _get_api_key()},
            )
            body = response.json()
            status = body["status"]

            if status == "READY":
                logger.info(f"Deployment successful! {body["deploymentUrl"]}")
                return
            elif status == "ERROR":
                logger.error(f"Deployment failed: {body["errorMessage"]}")
                return
            elif status == "CANCELED":
                logger.warn(f"Deployment canceled: {body["errorMessage"]}")
                return

            time.sleep(POLLING_INTERVAL_SECONDS)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error while checking deployment status: {e}")
            return

    logger.warn("Timed out while monitoring deployment.")


def cleanup_build(build_path: str):
    """
    Clean up the Luma build by removing the temporary zip file located at `build_path`.

    Args
        build_path (str): The temporary file location of the zipped Luma project
    """
    if os.path.exists(build_path):
        os.unlink(build_path)
