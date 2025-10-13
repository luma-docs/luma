import json
import logging
import os
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config_resolution import ResolvedConfig
from .node import get_node_root

logger = logging.getLogger(__name__)


def link_static_asset(relative_path: str, project_root: str):
    src = os.path.join(project_root, relative_path)
    dst = os.path.join(get_node_root(project_root), "public", relative_path)

    if os.path.exists(dst):
        os.remove(dst)

    logger.debug(f"Linking file from '{src}' to '{dst}'")
    os.link(src, dst)


def link_config(resolved_config: ResolvedConfig, project_root: str):
    dst = os.path.join(get_node_root(project_root), "data", "config.json")
    data = resolved_config.model_dump()
    with open(dst, "w") as file:
        logger.debug(f"Writing `ResolvedConfig` object to {dst!r}")
        file.write(json.dumps(data, sort_keys=False))


def link_existing_pages(project_root: str):
    for dir_path, _, filenames in os.walk(project_root):
        for filename in filenames:
            if not filename.endswith(".md"):
                continue

            file_path = os.path.join(dir_path, filename)
            relative_path = os.path.relpath(file_path, project_root)
            if relative_path.startswith(".luma"):
                continue

            _link_page(project_root, relative_path)


def _link_page(project_root: str, relative_path: str):
    src = os.path.join(project_root, relative_path)
    dst = os.path.join(get_node_root(project_root), "pages", relative_path)

    if os.path.exists(dst):
        os.remove(dst)

    logger.debug(f"Linking page from '{src}' to '{dst}'")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.link(src, dst)


def link_page_on_creation(project_root: str):
    event_handler = _FileLinker(project_root)
    observer = Observer()
    observer.daemon = True
    observer.schedule(event_handler, path=project_root, recursive=True)
    observer.start()


class _FileLinker(FileSystemEventHandler):
    def __init__(self, project_root: str):
        self._project_root = Path(project_root)

    def on_created(self, event):
        if not event.is_directory:
            relative_path = Path(event.src_path).relative_to(self._project_root)
            if str(relative_path).startswith(".luma") or not str(
                relative_path
            ).endswith(".md"):
                return
            _link_page(self._project_root, relative_path)
