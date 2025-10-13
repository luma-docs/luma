import collections
import importlib
import logging
import os
from types import ModuleType

import typer

logger = logging.getLogger(__name__)


def get_project_root():
    project_root = os.getcwd()

    if not os.path.exists(os.path.join(project_root, "luma.yaml")):
        logger.error("The current directory isn't a valid Luma project.")
        raise typer.Exit(1)

    return project_root


def get_module_and_relative_name(fully_qualified_name: str) -> tuple[ModuleType, str]:
    """Return the module and name of the Python object relative to the module.

    This utility is necessary because you don't know which part of a fully qualified
    name is the module. For example, for the fully qualfied name  'spam.ham.eggs', you
    don't know if 'spam' or 'spam.ham' is the module ('ham' could be a class in the
    'spam' module with a 'eggs' method).

    Examples:
        >>> get_module_and_qualname("luma.examples.Account.deposit")
        (<module 'luma.examples' from '.../examples.py'>, 'Account.deposit')
    """
    segments = fully_qualified_name.split(".")
    assert len(segments) > 1, f"Invalid fully qualified name: {fully_qualified_name}"

    # Iteratively try to import the module until you find the correct module.
    qualname_start_index = len(segments) - 1
    while qualname_start_index > 0:
        module_name = ".".join(segments[:qualname_start_index])
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            qualname_start_index -= 1
        else:
            break

    if qualname_start_index == 0:
        raise ImportError(f"Couldn't import module: {module_name}")

    qualname = ".".join(segments[qualname_start_index:])
    return module, qualname


def get_obj(module: ModuleType, qualname: str) -> object:
    """Return the Python object with the given qualfied name.

    This utility function is necessary because the built-in `getattr` function doesn't
    support nested attributes.

    Examples:
        >>> import luma.examples
        >>> getattr(luma.examples, "Account.deposit")
        Traceback (most recent call last):
          ...
        AttributeError: module 'luma.examples' has no attribute 'Account.deposit'
        >>> get_obj(luma.examples, "Account.deposit")
        <function Account.deposit at 0x...>
    """
    segments = collections.deque(qualname.split("."))
    obj = module
    while segments:
        # Iteratively get the next attribute in the qualified name until you reach the
        # final object.
        attr = segments.popleft()
        try:
            obj = getattr(obj, attr)
        except AttributeError:
            raise ValueError(f"Couldn't get attribute: {attr}")

    return obj
