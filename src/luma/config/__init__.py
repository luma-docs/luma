"""Configuration models and utilities for Luma."""

from .user_config import (
    CONFIG_FILENAME,
    Config,
    Link,
    NavigationItem,
    Page,
    Reference,
    Section,
    create_or_update_config,
    load_config,
)
from .resolved_config import (
    ResolvedConfig,
    ResolvedLink,
    ResolvedPage,
    ResolvedReference,
    ResolvedTab,
    ResolvedSection,
)
from .resolution import resolve_config, resolve_page

__all__ = [
    # User-facing config
    "CONFIG_FILENAME",
    "Config",
    "Link",
    "NavigationItem",
    "Page",
    "Reference",
    "Section",
    "create_or_update_config",
    "load_config",
    # Resolved config
    "ResolvedConfig",
    "ResolvedLink",
    "ResolvedPage",
    "ResolvedReference",
    "ResolvedSection",
    # Resolution
    "resolve_config",
    "resolve_page",
]
