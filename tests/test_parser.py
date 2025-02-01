from luma.parser import _parse_func


def test_parse_func():
    def f(x: int, y: int) -> int:
        """This is the summary.

        This is the description.
        """
        return x + y

    definition = _parse_func(f)

    assert definition.summary == "This is the summary."
    assert definition.desc == "This is the description."


def test_parse_func_multi_line_summary():
    def f(x: int, y: int) -> int:
        """
        Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary
        SummarySummary

        This is the description.
        """
        return x + y

    definition = _parse_func(f)

    assert (
        definition.summary
        == "Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary SummarySummary"
    )
    assert definition.desc == "This is the description."


def test_parse_func_multi_line_summary_first_line():
    def f(x: int, y: int) -> int:
        """Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary
        SummarySummarySummary

        This is the description.
        """
        return x + y

    definition = _parse_func(f)

    assert (
        definition.summary
        == "Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary SummarySummarySummary"
    )
    assert definition.desc == "This is the description."


def test_parse_func_multiple_sections():
    def f(x: int, y: int) -> int:
        """Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary
        SummarySummarySummary

        This is the description.

        This is another section of the description.
        """
        return x + y

    definition = _parse_func(f)

    assert (
        definition.summary
        == "Summary SummarySummarySummarySummarySummarySummarySummarySummarySummarySummarySummary SummarySummarySummary"
    )
    assert (
        definition.desc
        == "This is the description.\n\nThis is another section of the description."
    )


def test_parse_func_no_summary():
    def f(x: int, y: int) -> int:
        """

        This is the description.
        """
        return x + y

    definition = _parse_func(f)

    # TODO: treat this as description instead of summary
    assert definition.summary == "This is the description."
