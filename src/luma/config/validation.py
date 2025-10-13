"""Validation utilities for config files."""

import logging
import os

from ..utils import get_module_and_relative_name, get_obj

logger = logging.getLogger(__name__)


def validate_page_exists(path: str, project_root: str) -> None:
    """Validate that a page file exists and is a markdown file.

    Args:
        path: The relative path to the page
        project_root: The project root directory

    Raises:
        ValueError: If the page doesn't exist or isn't a markdown file
    """
    if path.startswith(("http://", "https://")):
        return

    local_path = os.path.join(project_root, path)
    if not os.path.exists(local_path):
        raise ValueError(
            f"Your config references a page at '{path}', but the file doesn't "
            "exist. Create the file or update the config to point to an existing file."
        )

    if not path.endswith(".md"):
        raise ValueError(
            f"Your config references a page at '{path}', but the file isn't a "
            "Markdown file. Luma only supports Markdown files."
        )


def validate_favicon_exists(favicon_path: str, project_root: str) -> None:
    """Validate that a favicon file exists.

    Args:
        favicon_path: The relative path to the favicon
        project_root: The project root directory

    Raises:
        ValueError: If the favicon doesn't exist
    """
    local_path = os.path.join(project_root, favicon_path)
    if not os.path.exists(local_path):
        raise ValueError(
            f"Your config specifies a favicon at '{favicon_path}', but the file doesn't "
            "exist. Create the file or update the config to point to an existing file."
        )


def validate_api_reference(qualname: str) -> None:
    """Validate that an API reference can be imported.

    Args:
        qualname: The fully qualified name of the API object

    Raises:
        ValueError: If the API object cannot be imported or found
    """
    try:
        module, relative_name = get_module_and_relative_name(qualname)
    except ImportError:
        package_name = qualname.split(".")[0]
        raise ValueError(
            f"Your config references '{qualname}', but Luma couldn't import the "
            f"package '{package_name}'. Make sure the module is installed in the "
            "current environment."
        )

    try:
        get_obj(module, relative_name)
    except AttributeError:
        raise ValueError(
            f"Your config references '{qualname}'. Luma imported the module "
            f"'{module.__name__}', but couldn't get the object '{relative_name}'. Are "
            "you sure the referenced object exists?"
        )
