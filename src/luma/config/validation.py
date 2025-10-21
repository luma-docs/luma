"""Validation utilities for config files."""

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List

from ..utils import get_module_and_relative_name, get_obj

if TYPE_CHECKING:
    from .user_config import Config

logger = logging.getLogger(__name__)

SUPPORTED_SOCIAL_PLATFORMS = {"discord", "github", "twitter", "slack"}


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


def validate_socials(socials: List[Dict[str, str]]) -> None:
    """Validate social media platform entries.

    Args:
        socials: List of social media platform dictionaries

    Raises:
        ValueError: If any social entry is invalid
    """
    for social in socials:
        if len(social) != 1:
            raise ValueError(
                "Each social entry must have exactly one platform-url pair, "
                f"got: {social}"
            )

        platform = list(social.keys())[0]
        if platform not in SUPPORTED_SOCIAL_PLATFORMS:
            raise ValueError(
                f"Invalid social platform '{platform}'. Valid platforms are: "
                f"{', '.join(sorted(SUPPORTED_SOCIAL_PLATFORMS))}"
            )


def validate_references(apis: List[str]) -> None:
    """Validate a list of API references.

    Args:
        apis: List of fully qualified API names

    Raises:
        ValueError: If any API reference is invalid
    """
    for qualname in apis:
        validate_api_reference(qualname)


def validate_navigation(navigation: List[Any], project_root: str) -> None:
    """Validate all navigation items.

    Args:
        navigation: List of navigation items (can be strings, Sections, References, or Links)
        project_root: The project root directory

    Raises:
        ValueError: If any navigation item is invalid
    """
    # Import here to avoid circular imports
    from .user_config import Reference, Section

    for item in navigation:
        if isinstance(item, str):
            validate_page_exists(item, project_root)
        elif isinstance(item, Section):
            for subitem in item.contents:
                if isinstance(subitem, str):
                    validate_page_exists(subitem, project_root)
                elif isinstance(subitem, Reference):
                    validate_references(subitem.apis)
        elif isinstance(item, Reference):
            validate_references(item.apis)


def validate_config(config: "Config") -> None:
    """Validate an entire config object.

    Args:
        config: The config object to validate

    Raises:
        ValueError: If any part of the config is invalid
    """
    # Validate favicon if present
    if config.favicon is not None:
        validate_favicon_exists(config.favicon, config.project_root)

    # Validate navigation
    validate_navigation(config.navigation, config.project_root)

    # Validate socials if present
    if config.socials is not None:
        validate_socials(config.socials)
