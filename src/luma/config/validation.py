"""Validation utilities for config files."""

import logging
import os
from typing import TYPE_CHECKING

from ..utils import get_module_and_relative_name, get_obj

if TYPE_CHECKING:
    from .user_config import Config, Reference, Section

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


def validate_reference(reference: "Reference") -> None:
    """Validate that all API references in a Reference object can be imported.

    Args:
        reference: The Reference object to validate

    Raises:
        ValueError: If any API reference cannot be imported or found
    """
    for qualname in reference.apis:
        validate_api_reference(qualname)


def validate_config(config: "Config") -> None:
    """Validate a Config object comprehensively.

    This function performs all validation checks on the config:
    - Validates favicon exists (if specified)
    - Validates all pages exist
    - Validates all API references can be imported

    Args:
        config: The Config object to validate

    Raises:
        ValueError: If any validation check fails
    """
    # Validate favicon
    if config.favicon is not None:
        validate_favicon_exists(config.favicon, config.project_root)

    # Validate navigation items
    for item in config.navigation:
        if isinstance(item, str):
            # It's a Page (string path)
            validate_page_exists(item, config.project_root)
        elif hasattr(item, "section"):
            # It's a Section - need to import to avoid circular dependency
            from .user_config import Section

            if isinstance(item, Section):
                for subitem in item.contents:
                    if isinstance(subitem, str):
                        # Page inside section
                        validate_page_exists(subitem, config.project_root)
                    elif hasattr(subitem, "reference"):
                        # Reference inside section
                        from .user_config import Reference

                        if isinstance(subitem, Reference):
                            validate_reference(subitem)
        elif hasattr(item, "reference"):
            # It's a top-level Reference
            from .user_config import Reference

            if isinstance(item, Reference):
                validate_reference(item)
