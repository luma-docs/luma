import importlib
import logging
import os
import platform
import zipfile
import json
import requests
import shutil
from typing import Optional
from .node import install_node_modules

REPO_OWNER = "luma-docs"
REPO_NAME = "luma"

logger = logging.getLogger(__name__)


def download_starter_files(path: str):
    _copy_files_from_luma_repo("starter/", path)


def download_or_update_scaffold(path: str) -> None:
    if not os.path.exists(path):
        _copy_files_from_luma_repo("app/", path, version=current_version)
        install_node_modules(path)
    else:
        current_version = importlib.metadata.version("luma-docs")
        scaffold_version = _get_scaffold_version(path)
        if current_version != scaffold_version:
            logger.info(
                f"You're using Luma {current_version}, but this project was last "
                f"updated with Luma {scaffold_version}. Updating project..."
            )
            shutil.rmtree(path)
            _copy_files_from_luma_repo("app/", path, version=current_version)
            install_node_modules(path)


def _get_scaffold_version(path: str) -> str:
    with open(os.path.join(path, "package.json")) as file:
        package_json = json.load(file)

    return package_json["version"]


def _copy_files_from_luma_repo(src: str, dst: str, version: Optional[str] = None):
    zip_path = os.path.join(_get_cache_dir(), "luma.zip")
    # TODO: Check if the ZIP file is already downloaded
    _download_luma_repo_as_zip(zip_path, version)
    with zipfile.ZipFile(zip_path) as zip_ref:
        # All files in the ZIP file are in a directory named after the repository.
        _copy_files_from_zip(os.path.join(f"{REPO_NAME}-main", src), dst, zip_ref)


def _get_cache_dir() -> str:
    system = platform.system()
    if system == "Windows":
        # Windows: Use %LOCALAPPDATA%
        base_dir = os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    elif system == "Darwin":
        # macOS: Use ~/Library/Caches
        base_dir = os.path.expanduser("~/Library/Caches")
    else:
        # Linux and other UNIX-like systems: Use ~/.cache
        base_dir = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

    cache_dir = os.path.join(base_dir, "luma")
    os.makedirs(cache_dir, exist_ok=True)  # Create the directory if it doesn't exist
    return cache_dir


def _download_luma_repo_as_zip(path: str, version: Optional[str] = None):
    # URL to download the repository as a ZIP file
    if version is None:
        url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/main.zip"
    else:
        url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/tags/{version}.zip"

    response = requests.get(url)
    if response.status_code != 200:
        logger.error(
            f"Failed to download ZIP file. HTTP Status code: {response.status_code}"
        )
        raise RuntimeError

    with open(path, "wb") as file:
        file.write(response.content)


def _copy_files_from_zip(src: str, dst: str, zip: zipfile.ZipFile):
    for file_name in zip.namelist():
        if file_name.startswith(src):
            relative_path = file_name[len(src) :]
            if not file_name.endswith("/"):
                destination_path = os.path.join(dst, relative_path)
                if os.path.exists(destination_path):
                    logger.warning(f"File '{destination_path}' already exists.")
                    continue

                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                with open(destination_path, "wb") as output_file:
                    output_file.write(zip.read(file_name))
