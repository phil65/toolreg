from __future__ import annotations

import importlib

from toolreg.registry.loaders.base import BaseLoader, LoaderError


class PluginLoader(BaseLoader):
    """Load tools from plugin modules."""

    name = "plugin"

    def can_load(self, source: str) -> bool:
        """Check if source is a valid plugin module."""
        try:
            module = importlib.import_module(source)
            return hasattr(module, "register_tools")
        except ImportError:
            return False

    def load(self, source: str) -> None:
        """Load tools from a plugin module."""
        if self.is_loaded(source):
            msg = f"Plugin {source} already loaded"
            raise LoaderError(msg)

        try:
            module = importlib.import_module(source)
            assert module
            # plugin loading logic here
            self._mark_loaded(source)
        except Exception as exc:
            msg = f"Failed to load plugin {source}"
            raise LoaderError(msg) from exc
