import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

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
                docs = _extract_page_content(
                    page_path, item.path, item.title, item.section, doc_type="page"
                )
                search_docs.extend(docs)
        elif isinstance(item, ResolvedReference):
            # Index API reference pages
            page_path = os.path.join(pages_path, item.relative_path)
            if os.path.exists(page_path):
                docs = _extract_page_content(
                    page_path,
                    item.relative_path,
                    item.title,
                    item.section,
                    doc_type="reference",
                )
                search_docs.extend(docs)

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


def _slugify(text: str) -> str:
    """Convert heading text to URL-friendly slug.

    Args:
        text: The heading text to slugify.

    Returns:
        URL-friendly slug.
    """
    # Convert to lowercase
    slug = text.lower()
    # Remove inline code backticks
    slug = re.sub(r"`([^`]+)`", r"\1", slug)
    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)
    # Remove non-alphanumeric chars except hyphens and dots
    slug = re.sub(r"[^\w.-]", "", slug)
    # Replace multiple consecutive hyphens with single hyphen
    slug = re.sub(r"-+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def _extract_page_content(
    file_path: str,
    relative_path: str,
    title: str,
    section: Optional[str],
    doc_type: str,
) -> List[Dict[str, Any]]:
    """Extract searchable content from a markdown file.

    Args:
        file_path: Absolute path to the markdown file.
        relative_path: Relative path for URL generation.
        title: Page title.
        section: Parent section name (if any).
        doc_type: Type of document ("page" or "reference").

    Returns:
        List of dictionaries with page/heading metadata for search indexing.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"Failed to read '{file_path}': {e}")
        return []

    # Generate base URL path
    url_path = "/" + relative_path.replace(".md", "")

    results = []

    # First, add entry for the page itself
    # Remove markdown syntax for cleaner content
    clean_content = re.sub(r"```[\s\S]*?```", "", content)
    clean_content = re.sub(r"`[^`]+`", "", clean_content)
    clean_content = re.sub(r"^#+\s+.+$", "", clean_content, flags=re.MULTILINE)
    clean_content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean_content)
    clean_content = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", clean_content)
    clean_content = re.sub(r"\s+", " ", clean_content).strip()
    content_preview = clean_content[:300] if clean_content else ""

    results.append(
        {
            "id": url_path,
            "title": title,
            "path": url_path,
            "content": content_preview,
            "section": section or "",
            "heading": "",
            "headingLevel": 0,
            "type": doc_type,
        }
    )

    # Extract individual headings (h1-h3) and create separate entries
    # Skip the first H1 to avoid duplicating the page-level entry
    headings = list(re.finditer(r"^(#{1,3})\s+(.+)$", content, re.MULTILINE))
    skip_first_h1 = True
    slug_counts: Dict[str, int] = {}  # Track slug usage to handle duplicates

    for match in headings:
        heading_level = len(match.group(1))
        heading_text = match.group(2).strip()

        # Skip the first H1 heading to avoid duplication with page entry
        if skip_first_h1 and heading_level == 1:
            skip_first_h1 = False
            continue

        heading_slug = _slugify(heading_text)

        # Handle duplicate slugs by appending a counter
        if heading_slug in slug_counts:
            slug_counts[heading_slug] += 1
            unique_slug = f"{heading_slug}-{slug_counts[heading_slug]}"
        else:
            slug_counts[heading_slug] = 1
            unique_slug = heading_slug

        results.append(
            {
                "id": f"{url_path}#{unique_slug}",
                "title": title,
                "path": f"{url_path}#{unique_slug}",
                "content": "",
                "section": section or "",
                "heading": heading_text,
                "headingLevel": heading_level,
                "type": doc_type,
            }
        )

    return results
