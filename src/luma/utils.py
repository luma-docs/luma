import logging
import os
import importlib
import typer
import yaml
from typing import Any, Optional

logger = logging.getLogger(__name__)


def get_project_root():
    project_root = os.getcwd()

    if not os.path.exists(os.path.join(project_root, "luma.yaml")):
        logger.error("The current directory isn't a valid Luma project.")
        raise typer.Exit(1)

    return project_root



