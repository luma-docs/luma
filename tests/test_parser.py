from luma.models import PyClass, PyFunc
from luma.parser import _parse_func, _parse_cls


def test_parse_func():
    def f(x: int, y: int) -> int:
        """This is the summary.

        This is the description.

        Args:
            x: The first argument.
            y: The second argument.

        Returns:
            The sum of x and y.
        """
        return x + y

    definition = _parse_func(f)

    assert definition == PyFunc(
        name="test_parser.test_parse_func.<locals>.f",
        signature="test_parser.test_parse_func.<locals>.f(x: int, y: int) -> int",
        summary="This is the summary.",
        desc="This is the description.",
        args=[
            {"name": "x", "type": None, "desc": "The first argument."},
            {"name": "y", "type": None, "desc": "The second argument."},
        ],
        returns="The sum of x and y.",
        examples=[],
    )


def test_parse_func_multi_line_summary():
    def f(x: int, y: int) -> int:
        """
        Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary
        SummarySummary

        This is the description.

        Args:
            x: The first argument.
            y: The second argument.

        Returns:
            The sum of x and y.
        """
        return x + y

    definition = _parse_func(f)

    assert definition == PyFunc(
        name="test_parser.test_parse_func_multi_line_summary.<locals>.f",
        signature="test_parser.test_parse_func_multi_line_summary.<locals>.f(x: int, y: int) -> int",
        summary="Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary SummarySummary",
        desc="This is the description.",
        args=[
            {"name": "x", "type": None, "desc": "The first argument."},
            {"name": "y", "type": None, "desc": "The second argument."},
        ],
        returns="The sum of x and y.",
        examples=[],
    )


def test_parse_func_multi_line_summary_first_line():
    def f(x: int, y: int) -> int:
        """Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary
        SummarySummarySummary

        This is the description.

        Args:
            x: The first argument.
            y: The second argument.

        Returns:
            The sum of x and y.
        """
        return x + y

    definition = _parse_func(f)

    assert definition == PyFunc(
        name="test_parser.test_parse_func_multi_line_summary_first_line.<locals>.f",
        signature="test_parser.test_parse_func_multi_line_summary_first_line.<locals>.f(x: int, y: int) -> int",
        summary="Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary SummarySummarySummary",
        desc="This is the description.",
        args=[
            {"name": "x", "type": None, "desc": "The first argument."},
            {"name": "y", "type": None, "desc": "The second argument."},
        ],
        returns="The sum of x and y.",
        examples=[],
    )


def test_parse_func_multiple_sections():
    def f(x: int, y: int) -> int:
        """Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary
        SummarySummarySummary

        This is the description.

        This is another section of the description.

        Args:
            x: The first argument.
            y: The second argument.

        Returns:
            The sum of x and y.
        """
        return x + y

    definition = _parse_func(f)

    assert definition == PyFunc(
        name="test_parser.test_parse_func_multiple_sections.<locals>.f",
        signature="test_parser.test_parse_func_multiple_sections.<locals>.f(x: int, y: int) -> int",
        summary="Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary SummarySummarySummary",
        desc="This is the description.\n\nThis is another section of the description.",
        args=[
            {"name": "x", "type": None, "desc": "The first argument."},
            {"name": "y", "type": None, "desc": "The second argument."},
        ],
        returns="The sum of x and y.",
        examples=[],
    )


def test_parse_func_no_summary():
    def f(x: int, y: int) -> int:
        """
        
        This is the description.

        Args:
            x: The first argument.
            y: The second argument.

        Returns:
            The sum of x and y.
        """
        return x + y

    definition = _parse_func(f)

    # TODO: treat this as description instead of summary
    assert definition == PyFunc(
        name="test_parser.test_parse_func_no_summary.<locals>.f",
        signature="test_parser.test_parse_func_no_summary.<locals>.f(x: int, y: int) -> int",
        summary="This is the description.",
        desc="",
        args=[
            {"name": "x", "type": None, "desc": "The first argument."},
            {"name": "y", "type": None, "desc": "The second argument."},
        ],
        returns="The sum of x and y.",
        examples=[],
    )
