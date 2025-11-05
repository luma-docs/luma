"""Config resolution logic.

Converts user-facing config into resolved config with inferred titles,
resolved paths, and validated references.
"""

import os
import re
from typing import Optional

import frontmatter

from .resolved_config import (
    ResolvedConfig,
    ResolvedLink,
    ResolvedPage,
    ResolvedReference,
    ResolvedSection,
    ResolvedSocial,
    ResolvedTab,
)
from .user_config import (
    Config,
    Link,
    NavigationItem,
    Page,
    Reference,
    Section,
    Social,
    Tab,
)


def resolve_config(config: Config, project_root: str) -> ResolvedConfig:
    """Convert user config to resolved config.

    Args:
        config: The user-facing config
        project_root: The project root directory

    Returns:
        The resolved config with inferred titles and validated references
    """
    resolved_navigation = [
        _resolve_navigation_item(item, project_root, section=None)
        for item in config.navigation
    ]

    resolved_socials = None
    if config.socials is not None:
        resolved_socials = _resolve_socials(config.socials)

    return ResolvedConfig(
        name=config.name,
        favicon=config.favicon,
        navigation=resolved_navigation,
        socials=resolved_socials,
    )


def _resolve_navigation_item(
    item: NavigationItem, project_root: str, section: Optional[str]
):
    """Resolve a single navigation item.

    Args:
        item: The navigation item to resolve
        project_root: The project root directory
        section: The section name if this item is inside a section, None otherwise

    Returns:
        The resolved navigation item
    """
    if isinstance(item, Page):
        return resolve_page(item, project_root, section=section)
    elif isinstance(item, Link):
        return _resolve_link(item)
    elif isinstance(item, Section):
        return _resolve_section(item, project_root)
    elif isinstance(item, Reference):
        return _resolve_reference(item, section=section)
    elif isinstance(item, Tab):
        return _resolve_tab(item, project_root)
    else:
        assert False, item


def _resolve_link(link: Link) -> ResolvedLink:
    """Resolve a link navigation item.

    Args:
        link: The link to resolve

    Returns:
        The resolved link with title
    """
    href = link.link

    title = link.title
    if title is None:
        title = href

    return ResolvedLink(href=href, title=title)


def _resolve_section(section: Section, project_root: str) -> ResolvedSection:
    """Resolve a section navigation item.

    Args:
        section: The section to resolve
        project_root: The project root directory

    Returns:
        The resolved section with resolved contents
    """
    resolved_contents = [
        _resolve_navigation_item(item, project_root, section=section.section)
        for item in section.contents
    ]
    return ResolvedSection(title=section.section, contents=resolved_contents)


def _resolve_tab(tab: Tab, project_root: str) -> ResolvedTab:
    """Resolve a tab navigation item.

    Args:
        tab: The tab to resolve
        project_root: The project root directory

    Returns:
        The resolved tab with resolved contents
    """
    resolved_contents = [
        _resolve_navigation_item(item, project_root, section=None)
        for item in tab.contents
    ]
    return ResolvedTab(title=tab.tab, contents=resolved_contents)


def _resolve_reference(
    reference: Reference, *, section: Optional[str] = None
) -> ResolvedReference:
    """Resolve a reference navigation item.

    Args:
        reference: The reference to resolve
        section: The section name if this reference is inside a section, None otherwise

    Returns:
        The resolved reference with generated path
    """
    relative_path = f"{reference.reference.lower().replace(' ', '-')}.md"
    return ResolvedReference(
        title=reference.reference,
        relative_path=relative_path,
        apis=reference.apis,
        section=section,
    )


def resolve_page(
    relative_path: str, project_root: str, *, section: Optional[str] = None
) -> ResolvedPage:
    """Resolve a page navigation item.

    Args:
        relative_path: The relative path to the page
        project_root: The project root directory
        section: The section name if this page is inside a section, None otherwise

    Returns:
        The resolved page with inferred title

    Raises:
        ValueError: If the page doesn't exist
    """
    local_path = os.path.join(project_root, relative_path)
    if not os.path.exists(local_path):
        raise ValueError(
            f"Page at '{relative_path}' doesn't exist in project root '{project_root}'"
        )

    title = _infer_title(local_path)
    return ResolvedPage(title=title, path=relative_path, section=section)


def _infer_title(local_path: str) -> str:
    """Infer the title of a page from its frontmatter or first heading.

    Args:
        local_path: The local path to the page

    Returns:
        The inferred title, or "Untitled Page" if no title is found
    """
    post = frontmatter.load(local_path)
    title = post.metadata.get("title", None)

    if title is None:
        title = _get_first_heading(local_path)

    if title is None:
        title = "Untitled Page"

    return title


def _get_first_heading(local_path: str) -> Optional[str]:
    """Get the first heading from a markdown file.

    Args:
        local_path: The local path to the markdown file

    Returns:
        The first heading text, or None if no heading is found
    """
    with open(local_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^(#{1,6})\s+(.*)", line.strip())
            if match:
                return match.group(2)  # the heading text
    return None


def _resolve_socials(socials: list[Social]) -> list[ResolvedSocial]:
    """Convert user-provided socials to resolved socials.

    Args:
        socials: List of social dicts, each with one platform-url pair

    Returns:
        List of ResolvedSocial objects
    """
    resolved = []
    for social in socials:
        platform, url = list(social.items())[0]
        resolved.append(ResolvedSocial(platform=platform, url=url))
    return resolved
