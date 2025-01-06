import logging
import os
import typer
import collections
import importlib
from types import ModuleType

logger = logging.getLogger(__name__)


def get_project_root():
    project_root = os.getcwd()

    if not os.path.exists(os.path.join(project_root, "luma.yaml")):
        logger.error("The current directory isn't a valid Luma project.")
        raise typer.Exit(1)

    return project_root


def get_module_and_qualname(fully_qualified_name: str) -> tuple[ModuleType, str]:
    segments = fully_qualified_name.split(".")
    assert len(segments) > 1, f"Invalid fully qualified name: {fully_qualified_name}"

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
    segments = collections.deque(qualname.split("."))
    obj = module
    while segments:
        attr = segments.popleft()
        try:
            obj = getattr(obj, attr)
        except AttributeError:
            raise ValueError(f"Couldn't get attribute: {attr}")

    return obj
