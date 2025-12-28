import importlib
import logging
import os
from typing import Optional

import typer
from typing_extensions import Annotated

from .bootstrap import download_or_update_scaffold, download_starter_files
from .config import (
    create_or_update_config,
    load_config,
    resolve_config,
)
from .deploy import (
    build_project,
    cleanup_build,
    deploy_project,
    monitor_deployment,
)
from .link import (
    link_config,
    link_existing_pages,
    link_first_page_to_index,
    link_page_on_creation,
    link_static_assets,
)
from .node import get_node_root, is_node_installed, run_node_dev
from .parser import prepare_references
from .search import build_search_index
from .utils import get_project_root

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
    download_or_update_scaffold(node_root)

    config = create_or_update_config(project_root, package_name)
    resolved_config = resolve_config(config, project_root=project_root)
    link_config(resolved_config, project_root)
    link_existing_pages(project_root)
    link_static_assets(project_root)
    build_search_index(project_root, resolved_config)


@app.command()
def dev(port: Annotated[Optional[int], typer.Option()] = None):
    project_root = get_project_root()

    node_root = get_node_root(project_root)
    download_or_update_scaffold(node_root)

    config = load_config(project_root)
    resolved_config = resolve_config(config, project_root=project_root)
    link_config(resolved_config, project_root)
    prepare_references(project_root, resolved_config)

    link_existing_pages(project_root)
    link_static_assets(project_root)
    link_first_page_to_index(project_root, resolved_config)
    build_search_index(project_root, resolved_config)
    link_page_on_creation(project_root)

    run_node_dev(project_root, port)


@app.command()
def deploy(version: Annotated[Optional[str], typer.Option("--version", "-v")] = None):
    project_root = get_project_root()

    node_root = get_node_root(project_root)
    download_or_update_scaffold(node_root)

    config = load_config(os.getcwd())
    resolved_config = resolve_config(config, project_root=project_root)
    prepare_references(project_root, resolved_config)

    link_config(resolved_config, project_root)
    link_existing_pages(project_root)
    link_static_assets(project_root)
    link_first_page_to_index(project_root, resolved_config)
    build_search_index(project_root, resolved_config)

    try:
        build_path = build_project(node_root)
        deploy_project(build_path, config.name, version)
        monitor_deployment(config.name)
    finally:
        cleanup_build(build_path)


def main():
    app()


if __name__ == "__main__":
    main()
