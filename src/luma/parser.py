import importlib
import inspect
import json
import logging
import os
import pkgutil
from types import FunctionType, ModuleType
from typing import Iterable

import yaml
from docstring_parser import parse

from .models import DocstringExample, PyArg, PyFunc, PyObj
from .node import get_node_root

logger = logging.getLogger(__name__)


# TODO: Merge with https://github.com/luma-docs/luma/pull/2.
def get_package_name(project_root: str) -> str:
    config_path = os.path.join(project_root, "luma.yaml")

    with open(config_path) as file:
        data = yaml.safe_load(file)
        return data["name"]


def prepare_references(project_root: str) -> None:
    package_name = get_package_name(project_root)
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        # TODO: Raise helpful error.
        raise

    from luma.utils import get_apis
    
    for qualname in get_apis():
        name = qualname.split(".")[-1]
        module_name = ".".join(qualname.split(".")[:-1])
        print(module_name)
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            logger.warning(f"Couldn't import '{module_name}'")
            continue

        try:
            obj = getattr(module, name)
        except AttributeError:
            logger.warning(f"Failed to get '{name}' from '{module.__name__}'")
            continue
        if isinstance(obj, FunctionType):
            api = _parse_func(obj)
            _write_api(api, project_root)

    # for sub_module in _iter_submodules(module):
        # yield from _parse_apis(sub_module)

    # for api in _parse_apis(package):
    #     _write_api(api, project_root)


def _parse_apis(module: ModuleType) -> Iterable[PyObj]:
    names = getattr(module, "__all__", [])
    for name in names:
        try:
            obj = getattr(module, name)
        except AttributeError:
            logger.warning(f"Failed to get '{name}' from '{module.__name__}'")
            continue
        if isinstance(obj, FunctionType):
            yield _parse_func(obj)

    for sub_module in _iter_submodules(module):
        yield from _parse_apis(sub_module)


def _parse_func(func: FunctionType) -> PyFunc:
    assert isinstance(func, FunctionType), func

    name = func.__module__ + "." + func.__qualname__
    signature = name + repr(inspect.signature(func))[len("<Signature ") : -len(">")]
    parsed = parse(func.__doc__)
    summary = parsed.short_description
    desc = parsed.long_description

    args = []
    for param in parsed.params:
        args.append(
            PyArg(name=param.arg_name, type=param.type_name, desc=param.description)
        )
    returns = parsed.returns.description if parsed.returns else None

    examples = []
    for example in parsed.examples:
        examples.append(DocstringExample(desc=None, code=example.description))

    return PyFunc(
        name=name,
        signature=signature,
        summary=summary,
        desc=desc,
        args=args,
        returns=returns,
        examples=examples,
    )


def _iter_submodules(package: ModuleType) -> Iterable[ModuleType]:
    if not _is_package(package):
        return

    for module_info in pkgutil.iter_modules(package.__path__):
        module_name = package.__name__ + "." + module_info.name
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            logger.warning(f"Couldn't import '{module_name}'")
            continue

        yield module


def _is_package(module: ModuleType) -> bool:
    return hasattr(module, "__path__")


def _write_api(api: PyObj, project_root: str) -> None:
    node_path = get_node_root(project_root)
    api_folder = os.path.join(node_path, "public", "api")
    if not os.path.exists(api_folder):
        os.makedirs(api_folder, exist_ok=True)

    filename = f"{api.name}.json"
    with open(os.path.join(api_folder, filename), "w") as f:
        logger.debug(f"Writing '{f.name}'")
        f.write(json.dumps(api.model_dump(), indent=4))
