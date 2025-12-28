"""Convert reStructuredText to Markdown.

This module provides utilities for converting RST-formatted text (commonly found in
Python docstrings) to Markdown format suitable for rendering in documentation.
"""

from typing import List, Optional

from docutils import nodes
from docutils.core import publish_doctree
from docutils.utils import SystemMessage


def convert_rst_to_markdown(rst_text: Optional[str]) -> Optional[str]:
    """Convert reStructuredText to Markdown.

    Args:
        rst_text: RST-formatted text to convert. Can be None.

    Returns:
        Markdown-formatted text, or None if input was None.
    """
    if rst_text is None:
        return None

    # Check if input contains newlines before stripping
    has_newlines = "\n" in rst_text
    rst_text = rst_text.strip()
    if not rst_text:
        # Empty/whitespace without newlines returns "", with newlines returns None
        return None if has_newlines else ""

    try:
        # Parse RST into docutils document tree
        import sys

        from docutils.parsers.rst import roles

        # Register Sphinx cross-reference roles
        def sphinx_ref_role(
            role, rawtext, text, lineno, inliner, options={}, content=[]
        ):
            """Convert Sphinx cross-references to reference nodes.

            :class:`module.MyClass` → [module.MyClass](module.MyClass)
            :class:`Custom <module.MyClass>` → [Custom](module.MyClass)
            """
            # Extract the actual reference text (handle `text <target>` syntax)
            if "<" in text and ">" in text:
                # Handle :class:`Custom Text <module.MyClass>`
                display_text = text[: text.index("<")].strip()
                target = text[text.index("<") + 1 : text.index(">")].strip()
            else:
                # Simple case: :class:`module.MyClass`
                display_text = text
                target = text

            # Create a reference node
            ref_node = nodes.reference(rawtext, display_text, refuri=target)
            return [ref_node], []

        # Register common Sphinx roles
        sphinx_roles_list = [
            "class",
            "func",
            "meth",
            "mod",
            "attr",
            "exc",
            "obj",
            "data",
            "const",
            "py:class",
            "py:func",
            "py:meth",
            "py:mod",
            "py:attr",
            "py:exc",
            "py:obj",
            "py:data",
            "py:const",
        ]
        for role_name in sphinx_roles_list:
            roles.register_local_role(role_name, sphinx_ref_role)

        doctree = publish_doctree(
            rst_text,
            settings_overrides={
                "report_level": 1,  # Suppress warnings
                "halt_level": 5,  # Don't halt on errors
                "Warning_stream": sys.stdout,
            },
        )

        # Convert document tree to Markdown
        visitor = MarkdownWriter(doctree)
        doctree.walkabout(visitor)

        result = "".join(visitor.output).strip()
        return result if result else None

    except SystemMessage:
        # If RST parsing fails, return the original text
        raise
        return rst_text


class MarkdownWriter(nodes.NodeVisitor):
    """Visitor that converts a docutils document tree to Markdown."""

    def __init__(self, document: nodes.document):
        super().__init__(document)
        self.output: List[str] = []
        self._list_depth = 0
        self._in_list_item = False

    def unknown_visit(self, node: nodes.Node) -> None:
        """Called for node types without a specific visit method."""
        pass

    def unknown_departure(self, node: nodes.Node) -> None:
        """Called for node types without a specific depart method."""
        pass

    # === Paragraphs and basic text ===

    def visit_paragraph(self, node: nodes.Node) -> None:
        """Handle paragraph nodes."""
        if not self._in_list_item:
            # Don't add extra newlines inside list items
            if self.output and not self.output[-1].endswith("\n\n"):
                self.output.append("\n\n")

    def depart_paragraph(self, node: nodes.Node) -> None:
        """Finish paragraph."""
        if not self._in_list_item:
            self.output.append("\n\n")

    def visit_Text(self, node: nodes.Text) -> None:
        """Handle plain text nodes."""
        self.output.append(node.astext())

    # === Inline formatting ===

    def visit_emphasis(self, node: nodes.Node) -> None:
        """Handle italic text (*text*)."""
        self.output.append("*")

    def depart_emphasis(self, node: nodes.Node) -> None:
        """Finish italic text."""
        self.output.append("*")

    def visit_strong(self, node: nodes.Node) -> None:
        """Handle bold text (**text**)."""
        self.output.append("**")

    def depart_strong(self, node: nodes.Node) -> None:
        """Finish bold text."""
        self.output.append("**")

    def visit_literal(self, node: nodes.Node) -> None:
        """Handle inline code (``code``)."""
        self.output.append(f"`{node.astext()}`")
        raise nodes.SkipNode

    def visit_title_reference(self, node: nodes.Node) -> None:
        """Handle title references (`title`)."""
        self.output.append(f"`{node.astext()}`")
        raise nodes.SkipNode

    # === Code blocks ===

    def visit_literal_block(self, node: nodes.Node) -> None:
        """Handle code blocks (:: blocks)."""
        code = node.astext()
        # Add leading newline only if not already present
        prefix = "" if self.output and self.output[-1].endswith("\n\n") else "\n"
        self.output.append(f"{prefix}```python\n{code}\n```\n")
        raise nodes.SkipNode

    def visit_doctest_block(self, node: nodes.Node) -> None:
        """Handle doctest blocks (>>> ...)."""
        code = node.astext()
        self.output.append(f"\n```python\n{code}\n```\n")
        raise nodes.SkipNode

    # === Lists ===

    def visit_bullet_list(self, node: nodes.Node) -> None:
        """Handle bullet lists."""
        self._list_depth += 1
        # Add newlines before top-level lists and nested lists
        if self.output and not self.output[-1].endswith("\n\n"):
            if self._list_depth == 1:
                # Top-level list needs spacing from previous content
                self.output.append("\n\n")
            elif self._list_depth > 1:
                # Nested list needs spacing from parent list item text
                self.output.append("\n\n")

    def depart_bullet_list(self, node: nodes.Node) -> None:
        """Finish bullet list."""
        self._list_depth -= 1
        if self._list_depth == 0:
            self.output.append("\n")

    def visit_enumerated_list(self, node: nodes.Node) -> None:
        """Handle numbered lists."""
        self._list_depth += 1
        # Add newlines before top-level lists and nested lists
        if self.output and not self.output[-1].endswith("\n\n"):
            if self._list_depth == 1:
                # Top-level list needs spacing from previous content
                self.output.append("\n\n")
            elif self._list_depth > 1:
                # Nested list needs spacing from parent list item text
                self.output.append("\n\n")

    def depart_enumerated_list(self, node: nodes.Node) -> None:
        """Finish numbered list."""
        self._list_depth -= 1
        if self._list_depth == 0:
            self.output.append("\n")

    def visit_list_item(self, node: nodes.Node) -> None:
        """Handle list items."""
        indent = "  " * (self._list_depth - 1)
        # Determine if parent is bullet or enumerated list
        if isinstance(node.parent, nodes.bullet_list):
            self.output.append(f"{indent}- ")
        else:  # enumerated_list
            self.output.append(f"{indent}1. ")
        self._in_list_item = True

    def depart_list_item(self, node: nodes.Node) -> None:
        """Finish list item."""
        # Only add newline if not already present (nested lists already add one)
        if not self.output or not self.output[-1].endswith("\n"):
            self.output.append("\n")
        self._in_list_item = False

    # === Links ===

    def visit_reference(self, node: nodes.Node) -> None:
        """Handle hyperlinks."""
        if "refuri" in node:
            text = node.astext()
            uri = node["refuri"]
            self.output.append(f"[{text}]({uri})")
            raise nodes.SkipNode

    # === Admonitions (directives) ===

    def _handle_admonition(self, node: nodes.Node, callout_type: str) -> None:
        """Handle admonition directives using Markdoc callout syntax.

        Args:
            node: The admonition node
            callout_type: One of 'note', 'warning', or 'tip' (Markdoc-supported types)
        """
        self.output.append(f"{{% {callout_type} %}}")
        # Walk children to preserve formatting (don't use astext())
        for child in node.children:
            child.walkabout(self)
        self.output.append(f"{{% /{callout_type} %}}")
        raise nodes.SkipNode

    def visit_warning(self, node: nodes.Node) -> None:
        """Handle .. warning:: directive."""
        self._handle_admonition(node, "warning")

    def visit_note(self, node: nodes.Node) -> None:
        """Handle .. note:: directive."""
        self._handle_admonition(node, "note")

    def visit_tip(self, node: nodes.Node) -> None:
        """Handle .. tip:: directive."""
        self._handle_admonition(node, "tip")

    def visit_important(self, node: nodes.Node) -> None:
        """Handle .. important:: directive (map to note)."""
        self._handle_admonition(node, "note")

    def visit_caution(self, node: nodes.Node) -> None:
        """Handle .. caution:: directive (map to warning)."""
        self._handle_admonition(node, "warning")

    def visit_attention(self, node: nodes.Node) -> None:
        """Handle .. attention:: directive (map to warning)."""
        self._handle_admonition(node, "warning")

    def visit_danger(self, node: nodes.Node) -> None:
        """Handle .. danger:: directive (map to warning)."""
        self._handle_admonition(node, "warning")

    def visit_error(self, node: nodes.Node) -> None:
        """Handle .. error:: directive (map to warning)."""
        self._handle_admonition(node, "warning")

    def visit_hint(self, node: nodes.Node) -> None:
        """Handle .. hint:: directive (map to tip)."""
        self._handle_admonition(node, "tip")

    # === Block quotes ===

    def visit_block_quote(self, node: nodes.Node) -> None:
        """Handle block quotes."""
        content = node.astext()
        lines = content.split("\n")
        self.output.append("\n\n")
        for line in lines:
            self.output.append(f"> {line}\n")
        self.output.append("\n")
        raise nodes.SkipNode
