import json
import logging
import os
from pathlib import Path

from pathspec import PathSpec
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import ResolvedConfig
from .node import get_node_root
from .rst_converter import convert_rst_to_markdown

STATIC_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico", ".svg")
logger = logging.getLogger(__name__)


def link_config(resolved_config: ResolvedConfig, project_root: str):
    dst = os.path.join(get_node_root(project_root), "data", "config.json")
    data = resolved_config.model_dump()
    with open(dst, "w") as file:
        logger.debug(f"Writing `ResolvedConfig` object to {dst!r}")
        file.write(json.dumps(data, sort_keys=False))


def link_existing_pages(project_root: str):
    for dir_path, _, filenames in os.walk(project_root):
        for filename in filenames:
            if not (filename.endswith(".md") or filename.endswith(".rst")):
                continue

            file_path = os.path.join(dir_path, filename)
            relative_path = os.path.relpath(file_path, project_root)
            if relative_path.startswith(".luma"):
                continue

            _link_page(project_root, relative_path)


def _link_page(project_root: str, relative_path: str):
    src = os.path.join(project_root, relative_path)

    # For RST files, convert to Markdown and write to .md file
    if relative_path.endswith(".rst"):
        # Read RST content
        with open(src, "r", encoding="utf-8") as f:
            rst_content = f.read()

        # Convert to Markdown
        md_content = convert_rst_to_markdown(rst_content)
        if md_content is None:
            md_content = ""

        # Write to .md file in .luma/pages/
        # Replace .rst extension with .md
        md_relative_path = relative_path[:-4] + ".md"
        dst = os.path.join(get_node_root(project_root), "pages", md_relative_path)

        if os.path.exists(dst):
            os.remove(dst)

        logger.debug(f"Converting and writing RST page from '{src}' to '{dst}'")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(md_content)
    else:
        # For Markdown files, create hard link as before
        dst = os.path.join(get_node_root(project_root), "pages", relative_path)

        if os.path.exists(dst):
            os.remove(dst)

        logger.debug(f"Linking page from '{src}' to '{dst}'")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.link(src, dst)


def link_static_assets(project_root: str):
    ignore_spec = _load_ignore_spec(project_root)

    for dir_path, _, filenames in os.walk(project_root):
        for filename in filenames:
            if not filename.endswith(STATIC_EXTENSIONS):
                continue

            file_path = os.path.join(dir_path, filename)
            relative_path = os.path.relpath(file_path, project_root)
            if relative_path.startswith(".luma"):
                continue

            if not ignore_spec or not ignore_spec.match_file(relative_path):
                _link_static_asset(project_root, relative_path)


def _load_ignore_spec(project_root: str):
    ignore_path = os.path.join(project_root, ".gitignore")

    if not os.path.exists(ignore_path):
        logger.debug("No .gitignore found")
        return None

    with open(ignore_path, "r") as file:
        return PathSpec.from_lines("gitwildmatch", file)


def _link_static_asset(project_root: str, relative_path: str):
    src = os.path.join(project_root, relative_path)
    dst = os.path.join(get_node_root(project_root), "public", relative_path)

    if os.path.exists(dst):
        os.remove(dst)

    logger.debug(f"Linking file from '{src}' to '{dst}'")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.link(src, dst)


def link_page_on_creation(project_root: str):
    event_handler = _FileLinker(project_root)
    observer = Observer()
    observer.daemon = True
    observer.schedule(event_handler, path=project_root, recursive=True)
    observer.start()


def link_first_page_to_index(project_root: str, config: ResolvedConfig):
    first_page = _get_first_page_path(config.navigation)

    # Check if it's an RST file that needs conversion
    if first_page.endswith(".rst"):
        # For RST files, copy the already-converted markdown from .luma/pages/
        md_first_page = first_page[:-4] + ".md"
        converted_src = os.path.join(get_node_root(project_root), "pages", md_first_page)
        dst = os.path.join(get_node_root(project_root), "pages", "index.md")

        if os.path.exists(dst):
            os.remove(dst)

        logger.debug(f"Copying converted RST page from '{converted_src}' to '{dst}'")
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        with open(converted_src, "r", encoding="utf-8") as f:
            content = f.read()
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        # For Markdown files, create hard link as before
        src = os.path.join(project_root, first_page)
        dst = os.path.join(get_node_root(project_root), "pages", "index.md")

        if os.path.exists(dst):
            os.remove(dst)

        logger.debug(f"Linking page from '{src}' to '{dst}'")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.link(src, dst)


def _get_first_page_path(items):
    for item in items:
        if item.type == "page":
            return item.path
        elif item.type == "section":
            return _get_first_page_path(item.contents)
        elif item.type == "tab":
            return _get_first_page_path(item.contents)
        elif item.type == "reference":
            return item.relative_path


class _FileLinker(FileSystemEventHandler):
    def __init__(self, project_root: str):
        self._project_root = Path(project_root)

    def on_created(self, event):
        if not event.is_directory:
            relative_path = Path(event.src_path).relative_to(self._project_root)
            relative_path_str = str(relative_path)
            if relative_path_str.startswith(".luma"):
                return
            if not (
                relative_path_str.endswith(".md") or relative_path_str.endswith(".rst")
            ):
                return
            _link_page(str(self._project_root), relative_path_str)

    def on_modified(self, event):
        """Handle file modifications - re-convert RST files when they change."""
        if not event.is_directory:
            relative_path = Path(event.src_path).relative_to(self._project_root)
            relative_path_str = str(relative_path)
            # Only re-process RST files on modification
            # Markdown files use hard links, so changes are automatically reflected
            if relative_path_str.startswith(".luma"):
                return
            if not relative_path_str.endswith(".rst"):
                return
            _link_page(str(self._project_root), relative_path_str)
