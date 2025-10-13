import importlib
import json
import logging
import os
import shutil
from importlib.resources import files

import pathspec

from .node import install_node_modules

REPO_OWNER = "luma-docs"
REPO_NAME = "luma"
BUCKET_URL = "https://luma-docs.s3.us-east-1.amazonaws.com/"

logger = logging.getLogger(__name__)


def download_starter_files(path: str):
    _copy_package_data("starter", path)


def download_or_update_scaffold(path: str) -> None:
    cli_version = _get_cli_version()

    should_download_scaffold = False
    # Check if the scaffold directory already exists.
    if os.path.exists(path):
        scaffold_version = _get_scaffold_version(path)
        if cli_version != scaffold_version:
            # Scaffold directory is outdated. Delete it and redownload the files.
            logger.info(
                f"You're using Luma {cli_version}, but this project was last "
                f"updated with Luma {scaffold_version}. Updating project..."
            )
            shutil.rmtree(path)
            should_download_scaffold = True

    else:
        # Scaffold directory doesn't exist. Download the files.
        should_download_scaffold = True

    if should_download_scaffold:
        _copy_package_data("app", path)
        install_node_modules(path)


def _get_scaffold_version(path: str) -> str:
    assert os.path.exists(path)

    with open(os.path.join(path, "package.json")) as file:
        package_json = json.load(file)

    return package_json["version"]


def _get_cli_version():
    version = importlib.metadata.version("luma-docs")
    assert version is not None
    return version


def _copy_package_data(rel: str, dst: str):
    """Copy files from the Luma source code directory.

    Args:
        rel: A path relative to the Luma source code directory.
        dst: The destination directory where this function will copy files into.
    """
    src = files("luma") / rel
    logger.debug(f"Copying package data from '{src}' to '{dst}'")

    # Load .gitignore rules
    gitignore_file = src / ".gitignore"
    spec = pathspec.PathSpec.from_lines(
        "gitwildmatch", gitignore_file.read_text().splitlines()
    )

    for file in src.rglob("*"):
        if file.is_file():
            rel = file.relative_to(src)
            if not spec.match_file(str(rel)):
                target = dst / file.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, target)
