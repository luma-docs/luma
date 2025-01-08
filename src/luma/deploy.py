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
    api_key = keyring.get_password("ike", "api_key")

    if not api_key:
        api_key = typer.prompt("Enter API key", hide_input=True)
        keyring.set_password("ike", "api_key", api_key)

    return api_key


def _load_ignore_spec(node_root: str) -> PathSpec:
    ignore_path = os.path.join(node_root, ".gitignore")

    if not os.path.exists(ignore_path):
        logger.error("Missing .gitignore in node root.")
        raise typer.Exit(1)

    with open(ignore_path, "r") as file:
        return PathSpec.from_lines("gitwildmatch", file)


def build_project(node_root: str) -> str:
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
    if os.path.exists(build_path):
        os.unlink(build_path)
