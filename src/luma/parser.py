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
from .config import Config, Reference, Section

logger = logging.getLogger(__name__)


def prepare_references(project_root: str, config: Config) -> None:
    for qualname in _list_api_qualnames(config):
        module_name, attr_name = qualname.rsplit(".", 1)

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            logger.warning(f"Couldn't import '{module_name}'")
            continue

        try:
            obj = getattr(module, attr_name)
        except AttributeError:
            logger.warning(f"Failed to get '{attr_name}' from '{module.__name__}'")
            continue
    
        if isinstance(obj, FunctionType):
            api = _parse_func(obj)
            _write_api(api, project_root)


def _list_api_qualnames(config: Config) -> Iterable[str]:
    for item in config.navigation:
        if isinstance(item, Reference):
            yield item.ref
        if isinstance(item, Section):
            for sub_item in item.contents:
                if isinstance(sub_item, Reference):
                    yield sub_item.ref


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


def _write_api(api: PyObj, project_root: str) -> None:
    node_path = get_node_root(project_root)
    api_folder = os.path.join(node_path, "public", "api")
    if not os.path.exists(api_folder):
        os.makedirs(api_folder, exist_ok=True)

    filename = f"{api.name}.json"
    with open(os.path.join(api_folder, filename), "w") as f:
        logger.debug(f"Writing '{f.name}'")
        f.write(json.dumps(api.model_dump(), indent=4))
