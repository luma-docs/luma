import importlib
import logging
import os
from typing import Optional

import typer
import yaml
from typing_extensions import Annotated

from .bootstrap import download_node_code, download_starter_files
from .deploy import build_project, cleanup_build, deploy_project, monitor_deployment
from .link import link_config_file, link_existing_pages, link_page_on_creation
from .node import get_node_root, install_node_modules, is_node_installed, run_node_dev
from .parser import prepare_references
from .utils import get_package_name, get_project_root

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command()
def init():
    if not is_node_installed():
        logger.error(
            "Luma depends on Node.js. Make sure it's installed in the current "
            "environment and available in the PATH."
        )
        raise typer.Exit(1)

    package_name = typer.prompt("What's the name of your package?")

    try:
        importlib.import_module(package_name)
    except ImportError:
        logger.error(
            f"Luma couldn't import a package named '{package_name}'. Make sure it's "
            "installed in the current environment."
        )
        raise typer.Exit(1)

    project_root = os.path.join(os.getcwd(), "docs/")
    node_root = get_node_root(project_root)

    logger.info(f"Initializing project directory to '{project_root}'.")
    download_starter_files(project_root)
    download_node_code(node_root)

    _insert_package_name_in_config(project_root, package_name)
    install_node_modules(node_root)
    link_config_file(project_root)
    link_existing_pages(project_root)


def _insert_package_name_in_config(project_root: str, package_name: str):
    # TODO: Refactor. This code is garbage.
    config_path = os.path.join(project_root, "luma.yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    config = {"name": package_name, **config}
    with open(config_path, "w") as file:
        yaml.dump(config, file, default_flow_style=False)


@app.command()
def dev(port: Annotated[Optional[int], typer.Option()] = None):
    project_root = get_project_root()

    node_root = get_node_root(project_root)
    if not os.path.exists(node_root):
        download_node_code(node_root)
        install_node_modules(node_root)

    prepare_references(project_root)
    link_config_file(project_root)
    link_existing_pages(project_root)
    link_page_on_creation(project_root)
    run_node_dev(project_root, port)


@app.command()
def deploy():
    node_root = get_node_root(get_project_root())
    package_name = get_package_name()

    try:
        build_path = build_project(node_root)
        deployment_id = deploy_project(build_path, package_name)
        monitor_deployment(deployment_id, package_name)
    finally:
        cleanup_build(build_path)


def main():
    app()


if __name__ == "__main__":
    main()
