import os
import re
from typing import Optional

import frontmatter

from .config import Config, Link, NavigationItem, Page, Reference, Section
from .resolved_config import (
    ResolvedConfig,
    ResolvedLink,
    ResolvedPage,
    ResolvedReference,
    ResolvedSection,
)


def resolve_config(config: Config, project_root: str):
    resolved_navigation = [
        _resolve_navigation_item(item, project_root) for item in config.navigation
    ]
    return ResolvedConfig(
        name=config.name, favicon=config.favicon, navigation=resolved_navigation
    )


def _resolve_navigation_item(item: NavigationItem, project_root: str):
    if isinstance(item, Page):
        return resolve_page(item, project_root)
    elif isinstance(item, Link):
        return _resolve_link(item)
    elif isinstance(item, Section):
        return _resolve_section(item, project_root)
    elif isinstance(item, Reference):
        return _resolve_reference(item)
    else:
        assert False, item


def _resolve_link(link: Link) -> ResolvedLink:
    href = link.link

    title = link.title
    if title is None:
        title = href

    return ResolvedLink(href=href, title=title)


def _resolve_section(section: Section, project_root: str) -> ResolvedSection:
    resolved_contents = [
        _resolve_navigation_item(item, project_root) for item in section.contents
    ]
    return ResolvedSection(title=section.section, contents=resolved_contents)


def _resolve_reference(reference: Reference):
    relative_path = f"{reference.reference.lower().replace(' ', '-')}.md"
    return ResolvedReference(
        title=reference.reference,
        relative_path=relative_path,
        apis=reference.apis,
    )


def resolve_page(relative_path: str, project_root: str):
    local_path = os.path.join(project_root, relative_path)
    if not os.path.exists(local_path):
        raise ValueError(...)

    title = _infer_title(local_path)
    return ResolvedPage(title=title, path=relative_path)


def _infer_title(local_path: str) -> str:
    post = frontmatter.load(local_path)
    title = post.metadata.get("title", None)

    if title is None:
        title = _get_first_heading(local_path)

    if title is None:
        title = "Untitled Page"

    return title


def _get_first_heading(local_path: str) -> Optional[str]:
    with open(local_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^(#{1,6})\s+(.*)", line.strip())
            if match:
                return match.group(2)  # the heading text
    return None
