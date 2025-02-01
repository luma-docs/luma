import inspect
import logging
import os
from types import FunctionType
from typing import Iterable, List, Tuple, Union

from docstring_parser import parse

from .config import Config, Reference, Section
from .models import DocstringExample, PyArg, PyClass, PyFunc, PyObj
from .node import get_node_root
from .utils import get_module_and_qualname, get_obj

logger = logging.getLogger(__name__)


def prepare_references(project_root: str, config: Config) -> None:
    for qualname in _list_api_qualnames(config):
        try:
            module, qualname = get_module_and_qualname(qualname)
        except ImportError:
            logger.warning(f"Couldn't import '{module.__name__}'")
            continue

        try:
            obj = get_obj(module, qualname)
        except AttributeError:
            logger.warning(f"Failed to get '{qualname}' from '{module.__name__}'")
            continue

        if isinstance(obj, FunctionType):
            func_info = _parse_func(obj)
            _write_page(func_info, project_root)
        elif isinstance(obj, type):
            cls_info = _parse_cls(obj)
            _write_page(cls_info, project_root)
            for method_info in cls_info.methods:
                _write_page(method_info, project_root)
        else:
            logger.warning(f"Unsupported API type: {type(obj)}")


def _list_api_qualnames(config: Config) -> Iterable[str]:
    for item in config.navigation:
        if isinstance(item, Reference):
            yield item.ref
        if isinstance(item, Section):
            for sub_item in item.contents:
                if isinstance(sub_item, Reference):
                    yield sub_item.ref


def _get_summary_and_desc(lines: List[str]) -> Tuple[str, str]:
    """Get summary and description from docstring lines.

    Given a list of lines in a docstring containing the summary and/or
    description, parse the lines and return the summary and description
    as separate strings. The description may contain multiple sections
    separated by blank newlines.

    Args:
        lines (str): the summary and description lines of the docstring,
                     split on newlines

    Returns:
        A tuple of (summary, description) formatted as single strings
    """
    summary = ""

    if len(lines) > 0:
        summary = " ".join([line.strip() for line in lines[0].split("\n")])

    sections = []

    if len(lines) > 1:
        for section in lines[1:]:
            sections.append(" ".join([line.strip() for line in section.split("\n")]))

    return summary.strip(), "\n\n".join(sections)


def _parse_func(func: FunctionType) -> PyFunc:
    assert isinstance(func, FunctionType), func

    name = func.__module__ + "." + func.__qualname__
    signature = _get_signature(func)
    parsed = parse(func.__doc__)
    lines = parsed.description.split("\n\n")
    summary, desc = _get_summary_and_desc(lines)

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


def _parse_cls(cls: type) -> PyClass:
    assert isinstance(cls, type), cls

    parsed = parse(cls.__doc__)
    body = parsed.description.split("\n\n")
    summary, desc = _get_summary_and_desc(body)

    examples = []
    for example in parsed.examples:
        examples.append(DocstringExample(desc=None, code=example.description))

    args = _parse_func(cls.__init__).args

    methods = []
    for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        # Ignore private methods
        if name.startswith("_"):
            continue

        methods.append(_parse_func(func))

    return PyClass(
        name=cls.__module__ + "." + cls.__qualname__,
        signature=_get_signature(cls),
        summary=summary,
        desc=desc,
        examples=examples,
        args=args,
        methods=methods,
    )


def _get_signature(obj: Union[FunctionType, type]) -> str:
    assert isinstance(obj, (FunctionType, type)), obj

    init_or_func = obj.__init__ if isinstance(obj, type) else obj
    name = obj.__module__ + "." + obj.__qualname__
    parameters: str = repr(inspect.signature(init_or_func))[
        len("<Signature ") : -len(">")
    ]

    # HACK: Remove 'self' parameter from class methods.
    if parameters.startswith("(self"):
        parameters = parameters.replace("(self, ", "(")

    return f"{name}{parameters}"


def _write_page(api: PyObj, project_root: str) -> None:
    node_path = get_node_root(project_root)
    reference_folder = os.path.join(node_path, "pages", "reference")
    os.makedirs(reference_folder, exist_ok=True)

    filename = f"{api.name}.md"
    with open(os.path.join(reference_folder, filename), "w") as f:
        logger.debug(f"Writing '{f.name}'")
        f.write(api.to_markdown())
