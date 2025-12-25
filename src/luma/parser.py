import inspect
import json
import logging
import os
import typing
from types import FunctionType
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from docstring_parser import Docstring, parse

from .config import ResolvedConfig, ResolvedReference, ResolvedSection, ResolvedTab
from .models import DocstringExample, PyArg, PyClass, PyFunc, PyObj
from .node import get_node_root
from .utils import get_module_and_relative_name, get_obj

logger = logging.getLogger(__name__)

MAX_FORMATTED_SIGNATURE_LENGTH = 80


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
                logger.warning(f"Couldn't import '{qualname}'")
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
        elif isinstance(item, ResolvedSection):
            for sub_item in item.contents:
                if isinstance(sub_item, ResolvedReference):
                    yield sub_item
        elif isinstance(item, ResolvedTab):
            for sub_item in item.contents:
                if isinstance(sub_item, ResolvedReference):
                    yield sub_item
                elif isinstance(sub_item, ResolvedSection):
                    for sub_sub_item in sub_item.contents:
                        if isinstance(sub_sub_item, ResolvedReference):
                            yield sub_sub_item


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
        # Preserve newlines within description paragraphs to maintain Markdown
        # formatting (lists, code blocks, etc.)
        desc = "\n\n".join(paragraph for paragraph in desc_paragraphs)
        desc = desc.strip() or None

    return summary, desc


def _parse_func(func: FunctionType, qualname: str) -> PyFunc:
    assert isinstance(func, FunctionType), func

    signature = format_signature(func, qualname)
    parsed = parse(func.__doc__)
    summary, desc = _get_summary_and_desc(parsed)
    param_types = _get_param_types(func)

    args = []
    for param in parsed.params:
        args.append(
            PyArg(
                name=param.arg_name,
                type=param_types.get(param.arg_name, param.type_name),
                desc=param.description,
            )
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
        signature=format_signature(cls, qualname),
        summary=summary,
        desc=desc,
        examples=examples,
        args=args,
        methods=methods,
    )


def format_signature(obj: Union[FunctionType, type], name: str) -> str:
    assert isinstance(obj, (FunctionType, type)), obj

    init_or_func = obj.__init__ if isinstance(obj, type) else obj
    if init_or_func == object.__init__:
        # If you don't override the default constructor, `inspect.signature` looks like
        # 'cls(/, *args, **kwargs)'. To simplify, we special case this and just do
        # 'cls()'.
        return f"{name}()"

    signature = inspect.signature(init_or_func)

    # Build list of formatted parameters, excluding 'self'. Each element is a string
    # of the form 'name: type' or 'name' if no annotation is specified.
    formatted_parameters: list[str] = []
    previous_kind = None
    for parameter in signature.parameters.values():
        if parameter.name == "self":
            continue

        if parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and previous_kind == inspect.Parameter.POSITIONAL_ONLY:
            formatted_parameters.append("/")
        elif parameter.kind == inspect.Parameter.KEYWORD_ONLY and previous_kind != inspect.Parameter.KEYWORD_ONLY:
            if previous_kind == inspect.Parameter.POSITIONAL_ONLY:
                formatted_parameters.append("/")
            formatted_parameters.append("*")
            
        previous_kind = parameter.kind

        if parameter.annotation != inspect.Signature.empty:
            formatted_parameter = (
                f"{parameter.name}: {format_annotation(parameter.annotation)}"
            )
        else:
            formatted_parameter = parameter.name

        if parameter.default != inspect.Parameter.empty:
            formatted_parameter += " = " + repr(parameter.default)

        formatted_parameters.append(formatted_parameter)

    # Try single-line signature first.
    formatted_signature = f"{name}({', '.join(formatted_parameters)})"
    if signature.return_annotation != inspect.Signature.empty:
        formatted_signature += f" -> {format_annotation(signature.return_annotation)}"

    # If the signature is too long, wrap it at the commas.
    if len(formatted_signature) > MAX_FORMATTED_SIGNATURE_LENGTH:
        formatted_signature = f"{name}(\n"
        for formatted_parameter in formatted_parameters:
            formatted_signature += f"    {formatted_parameter},\n"
        formatted_signature += ")"

        if signature.return_annotation != inspect.Signature.empty:
            formatted_signature += (
                f" -> {format_annotation(signature.return_annotation)}"
            )

    return formatted_signature


def format_annotation(annotation: Any) -> str:
    # If the user provided a quoted type, used that quoted value directly.
    if isinstance(annotation, str):
        return annotation

    elif annotation is type(None):
        return "None"

    elif isinstance(annotation, typing.ForwardRef):
        # HACK
        return repr(annotation)[len("ForwardRef('") : -len("']")]

    elif repr(typing.get_origin(annotation)) == "typing.Union":
        return " | ".join(format_annotation(arg) for arg in typing.get_args(annotation))

    elif typing.get_origin(annotation) is not None:
        name = format_annotation(typing.get_origin(annotation))
        args = [format_annotation(arg) for arg in typing.get_args(annotation)]
        if args:
            return f"{name}[{', '.join(args)}]"
        else:
            return name

    elif hasattr(annotation, "__name__"):
        return annotation.__name__

    else:
        return repr(annotation)


def _get_param_types(obj: Union[FunctionType, type]) -> Dict[str, Optional[str]]:
    """Get parameter types from type hints specified in a function signature.

    Args:
        obj: The function to parse.

    Returns:
        A dictionary of parameter names mapped to signature type hints.
    """
    assert isinstance(obj, (FunctionType, type)), obj

    parameters = {}

    if not isinstance(obj, type):
        signature = inspect.signature(obj)

        for param_name, param in signature.parameters.items():
            annotation = _get_type_annotation(param)
            if annotation is not None:
                parameters[param_name] = annotation

    return parameters


def _get_type_annotation(param: inspect.Parameter) -> Optional[str]:
    if isinstance(param.annotation, str):
        annotation = param.annotation

    elif isinstance(param.annotation, type):
        annotation = param.annotation.__name__
        if annotation == "_empty":
            annotation = None

    else:
        annotation = None

    return annotation
