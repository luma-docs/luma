"""Configuration models and utilities for Luma."""

from .resolution import resolve_config, resolve_page
from .resolved_config import (
    ResolvedConfig,
    ResolvedLink,
    ResolvedPage,
    ResolvedReference,
    ResolvedSection,
    ResolvedTab,
)
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
    "ResolvedTab",
    # Resolution
    "resolve_config",
    "resolve_page",
]
