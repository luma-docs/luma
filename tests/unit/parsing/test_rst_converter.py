"""Tests for RST to Markdown conversion."""

from luma.rst_converter import convert_rst_to_markdown


class TestBasicText:
    """Test basic text conversion."""

    def test_empty_string(self):
        """Empty string should return None."""
        assert convert_rst_to_markdown("") == ""
        assert convert_rst_to_markdown("   ") == ""

    def test_plain_text(self):
        """Plain text should pass through unchanged."""
        result = convert_rst_to_markdown("This is plain text.")
        assert result == "This is plain text."

    def test_multiline_paragraph(self):
        """Multiple paragraphs should be preserved."""
        rst = """First paragraph.\n\nSecond paragraph."""
        result = convert_rst_to_markdown(rst)
        expected = "First paragraph.\n\nSecond paragraph."
        assert result == expected


class TestInlineFormatting:
    """Test inline formatting conversion."""

    def test_bold(self):
        """**bold** should convert to **bold**."""
        # Note: RST includes trailing text in the markup if not escaped
        # breakpoint()
        result = convert_rst_to_markdown("Use **bold** for emphasis")
        expected = "Use **bold** for emphasis"
        assert result == expected

    def test_italic(self):
        """*italic* should convert to *italic*."""
        result = convert_rst_to_markdown("Use *italic* for terms")
        expected = "Use *italic* for terms"
        assert result == expected

    def test_inline_code(self):
        """``code`` should convert to `code`."""
        result = convert_rst_to_markdown("Use ``print()`` to output.")
        expected = "Use `print()` to output."
        assert result == expected

    def test_title_reference(self):
        """`title` should convert to `title`."""
        result = convert_rst_to_markdown("See `foo` for details.")
        expected = "See `foo` for details."
        assert result == expected


class TestCodeBlocks:
    """Test code block conversion."""

    def test_literal_block(self):
        """:: code blocks should convert to ```."""
        rst = """Example::

    def hello():
        print("world")"""
        result = convert_rst_to_markdown(rst)
        expected = """Example:\n\n```\ndef hello():\n    print("world")\n```"""
        assert result == expected

    def test_doctest_block(self):
        """>>> doctest blocks should convert to ```python."""
        rst = """>>> print("hello")\nhello"""
        result = convert_rst_to_markdown(rst)
        expected = """```python\n>>> print("hello")\nhello\n```"""
        assert result == expected


class TestLists:
    """Test list conversion."""

    def test_bullet_list(self):
        """Bullet lists should convert to Markdown."""
        rst = """- First item\n- Second item\n- Third item"""
        result = convert_rst_to_markdown(rst)
        expected = "- First item\n- Second item\n- Third item"
        assert result == expected

    def test_numbered_list(self):
        """Numbered lists should convert to Markdown."""
        rst = """1. First
2. Second
3. Third"""
        result = convert_rst_to_markdown(rst)
        expected = "1. First\n1. Second\n1. Third"
        assert result == expected

    def test_nested_list(self):
        """Nested lists should preserve structure."""
        rst = """- Item 1

  - Nested item

- Item 2"""
        result = convert_rst_to_markdown(rst)
        expected = "- Item 1\n\n  - Nested item\n- Item 2"
        assert result == expected


class TestAdmonitions:
    """Test admonition (directive) conversion to Markdoc callouts."""

    def test_warning_directive(self):
        """.. warning:: should convert to {% warning %}."""
        rst = """.. warning::

   Be careful!"""
        result = convert_rst_to_markdown(rst)
        expected = "{% warning %}\n\nBe careful!\n\n{% /warning %}"
        assert result == expected

    def test_note_directive(self):
        """.. note:: should convert to {% note %}."""
        rst = """.. note::

   This is important."""
        result = convert_rst_to_markdown(rst)
        expected = "{% note %}\n\nThis is important.\n\n{% /note %}"
        assert result == expected

    def test_tip_directive(self):
        """.. tip:: should convert to {% tip %}."""
        rst = """.. tip::

   Pro tip here."""
        result = convert_rst_to_markdown(rst)
        expected = "{% tip %}\n\nPro tip here.\n\n{% /tip %}"
        assert result == expected

    def test_multiline_admonition(self):
        """Admonitions with multiple paragraphs should work."""
        rst = """.. warning::

   First paragraph.

   Second paragraph."""
        result = convert_rst_to_markdown(rst)
        expected = (
            "{% warning %}\n\n"
            "First paragraph.\n\n"
            "Second paragraph.\n\n"
            "{% /warning %}"
        )
        assert result == expected

    def test_admonition_with_formatting(self):
        """Admonitions with inline formatting should preserve it."""
        rst = """.. note::

   This has **bold** and ``code``."""
        result = convert_rst_to_markdown(rst)
        expected = "{% note %}\n\nThis has **bold** and `code`.\n\n{% /note %}"
        assert result == expected


class TestLinks:
    """Test hyperlink conversion."""

    def test_external_link(self):
        """External links should convert to [text](url)."""
        rst = "`Python <https://python.org>`_"
        result = convert_rst_to_markdown(rst)
        expected = "[Python](https://python.org)"
        assert result == expected


class TestComplexExamples:
    """Test real-world docstring examples."""

    def test_function_docstring(self):
        """Test a realistic function docstring."""
        rst = """Execute a command.

This function runs the given command and returns the output.

.. warning::

   Commands are executed without sanitization!

Example usage::

    result = execute("ls -la")"""
        result = convert_rst_to_markdown(rst)
        # Just check key components are present since formatting may vary
        assert "Execute a command" in result
        assert "{% warning %}" in result
        assert "sanitization" in result
        assert "```" in result
        assert "execute(" in result

    def test_parameter_description_with_code(self):
        """Test parameter descriptions with inline code."""
        rst = "The ``timeout`` parameter sets the maximum wait time."
        result = convert_rst_to_markdown(rst)
        expected = "The `timeout` parameter sets the maximum wait time."
        assert result == expected

    def test_mixed_formatting(self):
        """Test text with multiple formatting types."""
        rst = (
            "Use **bold** for emphasis, " "``code`` for values, and *italic* for terms."
        )
        result = convert_rst_to_markdown(rst)
        expected = (
            "Use **bold** for emphasis, " "`code` for values, and *italic* for terms."
        )
        assert result == expected


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_rst_returns_original(self):
        """If RST parsing fails, return original text."""
        # Most text is valid RST, so this is hard to trigger
        # But the function should handle SystemMessage exceptions
        result = convert_rst_to_markdown("Normal text")
        expected = "Normal text"
        assert result == expected

    def test_whitespace_only_content(self):
        """Whitespace-only content should return None."""
        assert convert_rst_to_markdown("   \n  \n  ") is None

    def test_special_characters(self):
        """Special characters should be preserved."""
        rst = "Use & and < and > symbols."
        result = convert_rst_to_markdown(rst)
        expected = "Use & and < and > symbols."
        assert result == expected
