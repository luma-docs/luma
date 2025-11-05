import json
import logging
import os
import re
from typing import Any, Dict, List

from .config import (
    ResolvedConfig,
    ResolvedPage,
    ResolvedReference,
    ResolvedSection,
    ResolvedTab,
)
from .node import get_node_root

logger = logging.getLogger(__name__)


def build_search_index(project_root: str, config: ResolvedConfig) -> None:
    """Build a search index from all documentation pages.

    Args:
        project_root: The root directory of the documentation project.
        config: The resolved configuration object.
    """
    node_path = get_node_root(project_root)
    pages_path = os.path.join(node_path, "pages")

    search_docs = []

    # Index regular documentation pages
    for item in _flatten_navigation(config.navigation):
        if isinstance(item, ResolvedPage):
            page_path = os.path.join(pages_path, item.path)
            if os.path.exists(page_path):
                doc = _extract_page_content(
                    page_path, item.path, item.title, item.section
                )
                if doc:
                    search_docs.append(doc)
        elif isinstance(item, ResolvedReference):
            # Index API reference pages
            page_path = os.path.join(pages_path, item.relative_path)
            if os.path.exists(page_path):
                doc = _extract_page_content(
                    page_path, item.relative_path, item.title, item.section
                )
                if doc:
                    search_docs.append(doc)

    # Write search index
    output_path = os.path.join(node_path, "data", "search-index.json")
    with open(output_path, "w") as f:
        logger.debug(f"Writing search index to '{output_path}'")
        json.dump(search_docs, f)


def _flatten_navigation(items: List[Any]) -> List[Any]:
    """Flatten the navigation tree into a list of pages and references.

    Args:
        items: List of navigation items (pages, sections, tabs, references).

    Returns:
        Flattened list of ResolvedPage and ResolvedReference objects.
    """
    result = []
    for item in items:
        if isinstance(item, (ResolvedPage, ResolvedReference)):
            result.append(item)
        elif isinstance(item, ResolvedSection):
            result.extend(_flatten_navigation(item.contents))
        elif isinstance(item, ResolvedTab):
            result.extend(_flatten_navigation(item.contents))
    return result


def _extract_page_content(
    file_path: str, relative_path: str, title: str, section: str | None
) -> Dict[str, Any] | None:
    """Extract searchable content from a markdown file.

    Args:
        file_path: Absolute path to the markdown file.
        relative_path: Relative path for URL generation.
        title: Page title.
        section: Parent section name (if any).

    Returns:
        Dictionary with page metadata and content for search indexing.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"Failed to read '{file_path}': {e}")
        return None

    # Extract headings (h1-h3)
    headings = []
    for match in re.finditer(r"^#{1,3}\s+(.+)$", content, re.MULTILINE):
        headings.append(match.group(1).strip())

    # Remove markdown syntax for cleaner content
    # Remove code blocks
    clean_content = re.sub(r"```[\s\S]*?```", "", content)
    # Remove inline code
    clean_content = re.sub(r"`[^`]+`", "", clean_content)
    # Remove headings
    clean_content = re.sub(r"^#+\s+.+$", "", clean_content, flags=re.MULTILINE)
    # Remove links but keep text
    clean_content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean_content)
    # Remove bold/italic
    clean_content = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", clean_content)
    # Remove extra whitespace
    clean_content = re.sub(r"\s+", " ", clean_content).strip()

    # Limit content to first 300 characters
    content_preview = clean_content[:300] if clean_content else ""

    # Generate URL path
    url_path = "/" + relative_path.replace(".md", "")

    return {
        "id": url_path,
        "title": title,
        "path": url_path,
        "headings": " ".join(headings),  # Join headings for indexing
        "content": content_preview,
        "section": section or "",
    }
