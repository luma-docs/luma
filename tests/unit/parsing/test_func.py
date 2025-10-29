import pytest

from luma.models import DocstringExample, PyArg, PyFunc, PyObjType
from luma.parser import parse_obj


def test_name():
    def f():
        pass

    definition = parse_obj(f, "g")

    # The parser should use the specified name rather than the actual name of the
    # function.
    assert definition.name == "g"


def test_type():
    def f():
        pass

    definition = parse_obj(f, "f")

    assert definition.type == PyObjType.FUNC


def test_one_line_summary():
    def f():
        """Summary."""

    definition = parse_obj(f, "f")

    assert definition.summary == "Summary."
    assert definition.desc is None


def test_one_line_summary_with_leading_newline():
    def f():
        """
        Summary.
        """

    definition = parse_obj(f, "f")

    assert definition.summary == "Summary."
    assert definition.desc is None


def test_multi_line_summary():
    def f(x: int, y: int) -> int:
        """One
        two.
        """
        return x + y

    definition = parse_obj(f, "f")

    assert definition.summary == "One two."
    assert definition.desc is None


def test_multi_line_summary_with_leading_newline():
    def f(x: int, y: int) -> int:
        """
        One
        two.
        """
        return x + y

    definition = parse_obj(f, "f")

    assert definition.summary == "One two."
    assert definition.desc is None


def test_desc_with_multiple_paragraphs():
    def f():
        """Summary.

        One.

        Two.
        """

    definition = parse_obj(f, "f")

    assert definition.desc == "One.\n\nTwo."


def test_desc_with_no_summary():
    def f():
        """

        This is the description.
        """

    definition = parse_obj(f, "f")

    # TODO: Treat this as description instead of summary
    assert definition.summary == "This is the description."


def test_single_example():
    def f():
        """

        Examples:
            >>> 0
            0
        """

    definition = parse_obj(f, "f")

    assert definition.examples == [DocstringExample(desc=None, code=">>> 0\n0")]


@pytest.mark.skip  # FIXME
def test_multiple_examples():
    def f():
        """

        Examples:
            >>> 0
            0

            >>> 1
            1
        """

    definition = parse_obj(f, "f")

    assert definition.examples == [
        DocstringExample(desc=None, code=">>> 0\n0"),
        DocstringExample(desc=None, code=">>>1\n1"),
    ]


def test_signature():
    def f(x: int) -> None:
        pass

    definition = parse_obj(f, "f")

    assert definition.signature == "f(x: int) -> None"


def test_args():
    def f(x: int):
        """

        Args:
            x: A number.
        """

    definition = parse_obj(f, "f")

    # TODO: Infer parameter type from the signature.
    assert definition.args == [PyArg(name="x", type="int", desc="A number.")]


def test_returns():
    def f():
        """

        Returns:
            Something.
        """

    definition = parse_obj(f, "f")

    assert definition.returns == "Something."


def test_type_annotation():
    def f(x: int):
        """

        Args:
            x:
        """
        pass

    definition = parse_obj(f, qualname="f")

    assert isinstance(definition, PyFunc)
    assert definition.args[0].type == "int"


def test_quoted_type_annotation():
    def f(x: "int"):
        """

        Args:
            x:
        """
        pass

    definition = parse_obj(f, qualname="f")

    assert isinstance(definition, PyFunc)
    assert definition.args[0].type == "int"


def test_comprehensive():
    def f(x: int, y: int) -> int:
        """This is the summary.

        This is the description.

        Args:
            x: The first number.
            y: The second number.

        Returns:
            The sum of x and y.

        Examples:
            >>> f(1, 2)
            3
        """
        return x + y

    definition = parse_obj(f, "f")

    assert definition.name == "f"
    assert definition.type == PyObjType.FUNC
    assert definition.summary == "This is the summary."
    assert definition.desc == "This is the description."
    assert definition.examples == [
        DocstringExample(
            desc=None,
            code=">>> f(1, 2)\n3",
        )
    ]
    assert definition.signature == "f(x: int, y: int) -> int"
    assert definition.args == [
        PyArg(name="x", type="int", desc="The first number."),
        PyArg(name="y", type="int", desc="The second number."),
    ]
    assert definition.returns == "The sum of x and y."
