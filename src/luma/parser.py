import inspect
import json
import logging
import os
from types import FunctionType
from typing import Any, Iterable, Optional, Tuple, Union

from docstring_parser import Docstring, parse

from .models import DocstringExample, PyArg, PyClass, PyFunc, PyObj
from .node import get_node_root
from .resolved_config import ResolvedConfig, ResolvedReference, ResolvedSection
from .utils import get_module_and_relative_name, get_obj

logger = logging.getLogger(__name__)


def prepare_references(project_root: str, config: ResolvedConfig) -> None:
    node_path = get_node_root(project_root)

    qualname_to_path = {}
    for reference in _list_references_in_config(config):
        markdown = f"# {reference.title}"

        for qualname in reference.apis:
            markdown += "\n\n---\n\n"
            try:
                module, relative_name = get_module_and_relative_name(qualname)
            except ImportError:
                logger.warning(f"Couldn't import '{module.__name__}'")
                continue

            try:
                obj = get_obj(module, relative_name)
            except AttributeError:
                logger.warning(
                    f"Failed to get '{relative_name}' from '{module.__name__}'"
                )
                continue

            obj_info = parse_obj(obj, qualname)
            markdown += obj_info.to_markdown()
            # HACK
            qualname_to_path[qualname] = (
                f"{reference.relative_path.replace('.md', '')}#{qualname}"
            )

        path = os.path.join(node_path, "pages", reference.relative_path)
        with open(path, "w") as f:
            logger.debug(f"Writing '{f.name}'")
            f.write(markdown)

    path = os.path.join(node_path, "data", "apis.json")
    with open(path, "w") as f:
        logger.debug(f"Writing '{f.name}'")
        f.write(json.dumps(qualname_to_path))


def parse_obj(obj: Any, qualname: str) -> PyObj:
    if isinstance(obj, FunctionType):
        return _parse_func(obj, qualname)
    elif isinstance(obj, type):
        return _parse_cls(obj, qualname)
    else:
        raise NotImplementedError(f"Unsupported API type: {type(obj)}")


def _list_references_in_config(config: ResolvedConfig) -> Iterable[ResolvedReference]:
    for item in config.navigation:
        if isinstance(item, ResolvedReference):
            yield item
        if isinstance(item, ResolvedSection):
            for sub_item in item.contents:
                if isinstance(sub_item, ResolvedReference):
                    yield sub_item


def _get_summary_and_desc(parsed: Docstring) -> Tuple[Optional[str], Optional[str]]:
    """Get summary and description from the parsed docstring.

    This function is necessary because, in the case where you have a summary stretch
    across two lines, `docstring_parser` thinks the second line is the description.

    Args:
        parsed: The parsed docstring.

    Returns:
        A tuple of (summary, description) formatted as either strings or `None`.
    """
    if parsed.description is None:
        return None, None

    paragraphs = parsed.description.split("\n\n")

    assert len(paragraphs) > 0
    summary_paragraph = paragraphs[0]
    summary = " ".join(summary_paragraph.split("\n")).strip() or None

    desc_paragraphs = paragraphs[1:]
    if not desc_paragraphs:
        desc = None
    else:
        desc = ""
        for i, paragraph in enumerate(desc_paragraphs):
            desc += " ".join(paragraph.split("\n")).strip()
            if i < len(desc_paragraphs) - 1:
                desc += "\n\n"
        if not desc:
            desc = None

    return summary, desc


def _parse_func(func: FunctionType, qualname: str) -> PyFunc:
    assert isinstance(func, FunctionType), func

    signature = _get_signature(func, qualname)
    parsed = parse(func.__doc__)
    summary, desc = _get_summary_and_desc(parsed)

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
        name=qualname,
        signature=signature,
        summary=summary,
        desc=desc,
        args=args,
        returns=returns,
        examples=examples,
    )


def _parse_cls(cls: type, qualname: str) -> PyClass:
    assert isinstance(cls, type), cls

    parsed = parse(cls.__doc__)
    # 'docstring_parser' doesn't handle multi-line summaries correctly, so we need to
    # manually extract the summary and description.
    summary, desc = _get_summary_and_desc(parsed)

    examples = []
    for example in parsed.examples:
        examples.append(DocstringExample(desc=None, code=example.description))

    if isinstance(cls.__init__, FunctionType):
        args = _parse_func(cls.__init__, qualname + "." + cls.__init__.__name__).args
    else:
        args = []

    methods = []
    for func_name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        # Ignore private methods
        if func_name.startswith("_"):
            continue

        methods.append(_parse_func(func, qualname + "." + func_name))

    return PyClass(
        name=qualname,
        signature=_get_signature(cls, qualname),
        summary=summary,
        desc=desc,
        examples=examples,
        args=args,
        methods=methods,
    )


def _get_signature(obj: Union[FunctionType, type], name: str) -> str:
    assert isinstance(obj, (FunctionType, type)), obj

    init_or_func = obj.__init__ if isinstance(obj, type) else obj
    if init_or_func == object.__init__:
        # If you don't override the default constructor, `inspect.signature` looks like
        # 'cls(/, *args, **kwargs)'. To simplify, we special case this and just do
        # 'cls()'.
        parameters = "()"
    else:
        parameters: str = repr(inspect.signature(init_or_func))[
            len("<Signature ") : -len(">")
        ]

    # HACK: Remove 'self' parameter from class methods.
    if parameters.startswith("(self"):
        parameters = parameters.replace("(self, ", "(")

    return f"{name}{parameters}"
