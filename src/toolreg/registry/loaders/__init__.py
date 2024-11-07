"""Tool loading functionality."""

from __future__ import annotations

import logging
from typing import ClassVar

from toolreg.registry.loaders.base import BaseLoader, LoaderError
from toolreg.registry.loaders.module_loader import ModuleLoader
from toolreg.registry.loaders.plugin_loader import PluginLoader
from toolreg.registry.loaders.toml_loader import TomlLoader


logger = logging.getLogger(__name__)


class ToolLoader:
    """Unified interface for loading tools from various sources."""

    _loaders: ClassVar[dict[str, type[BaseLoader]]] = {
        "toml": TomlLoader,
        "module": ModuleLoader,
        "plugin": PluginLoader,
    }

    def __init__(self) -> None:
        """Initialize the tool loader."""
        self._active_loaders: dict[str, BaseLoader] = {
            name: loader_cls() for name, loader_cls in self._loaders.items()
        }

    def load(self, source: str) -> None:
        """Load tools from the given source.

        This method automatically detects the appropriate loader to use.

        Args:
            source: Path or identifier to load from

        Raises:
            LoaderError: If no suitable loader is found or loading fails
        """
        for loader in self._active_loaders.values():
            if loader.can_load(source):
                try:
                    loader.load(source)
                except Exception as exc:
                    logger.exception("Loader %s failed for %s", loader.name, source)
                    msg = f"Failed to load {source} with {loader.name}"
                    raise LoaderError(msg) from exc
                else:
                    return

        msg = f"No suitable loader found for {source}"
        raise LoaderError(msg)

    def load_many(self, sources: list[str]) -> None:
        """Load tools from multiple sources.

        Args:
            sources: List of paths or identifiers to load from
        """
        for source in sources:
            try:
                self.load(source)
            except LoaderError:
                logger.exception("Failed to load %s", source)
