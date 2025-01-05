import logging
import os

import typer
import yaml

logger = logging.getLogger(__name__)


def get_project_root():
    project_root = os.getcwd()

    if not os.path.exists(os.path.join(project_root, "luma.yaml")):
        logger.error("The current directory isn't a valid Luma project.")
        raise typer.Exit(1)

    return project_root


def get_package_name() -> str:
    config_path = os.path.join(get_project_root(), "luma.yaml")

    with open(config_path) as file:
        try:
            data = yaml.safe_load(file)

            if "name" not in data:
                logger.error(
                    "Package name not found. Please add `name: <your_package_name>` to luma.yaml"
                )
                raise typer.Exit(1)

            return data["name"]
        except yaml.YAMLError as e:
            logger.error(f"Error parsing luma.yaml: {e}")
            raise typer.Exit(1)


def get_apis() -> str:
    config_path = os.path.join(get_project_root(), "luma.yaml")

    with open(config_path) as file:
        try:
            data = yaml.safe_load(file)

            if "name" not in data:
                logger.error(
                    "Package name not found. Please add `name: <your_package_name>` to luma.yaml"
                )
                raise typer.Exit(1)

            apis = set()
            nav = data["navigation"]
            for item in nav:
                if "ref" in item:
                    apis.add(item["ref"])
                elif "contents" in item:
                    for subitem in item["contents"]:
                        if "ref" in subitem:
                            apis.add(subitem["ref"])

            return apis
        except yaml.YAMLError as e:
            logger.error(f"Error parsing luma.yaml: {e}")
            raise typer.Exit(1)

