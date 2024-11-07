"""Tool loading functionality."""

from __future__ import annotations

import logging
from typing import ClassVar

from toolreg.registry import registry
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

    def __init__(self, registry_instance: registry.ToolRegistry | None = None) -> None:
        """Initialize the tool loader.

        Args:
            registry_instance: The registry to register tools in
        """
        reg = registry_instance or registry.ToolRegistry()
        self._active_loaders: dict[str, BaseLoader] = {
            name: loader_cls(reg) for name, loader_cls in self._loaders.items()
        }

    def load(self, source: str, *, recursive: bool = True) -> None:
        """Load tools from the given source."""
        for loader in self._active_loaders.values():
            if loader.can_load(source):
                try:
                    loader.load(source, recursive=recursive)  # type: ignore
                except Exception as exc:
                    logger.exception("Loader %s failed for %s", loader.name, source)
                    msg = f"Failed to load {source} with {loader.name}"
                    raise LoaderError(msg) from exc
                return

        msg = f"No suitable loader found for {source}"
        raise LoaderError(msg)

    def load_many(self, sources: list[str], *, recursive: bool = True) -> None:
        """Load tools from multiple sources."""
        for source in sources:
            try:
                self.load(source, recursive=recursive)
            except LoaderError:
                logger.exception("Failed to load %s", source)
