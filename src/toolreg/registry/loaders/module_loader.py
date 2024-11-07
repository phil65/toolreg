"""Python module based tool loader."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any

from toolreg.registry.loaders.base import BaseLoader, LoaderError


class ModuleLoader(BaseLoader):
    """Load tools from Python modules."""

    name = "module"

    def can_load(self, source: str) -> bool:
        """Check if source is a valid Python module path."""
        try:
            # Try to find the module without importing
            return bool(importlib.util.find_spec(source))
        except ModuleNotFoundError:
            return False

    def load(self, source: str, **kwargs: Any) -> None:
        """Load tools from a Python module."""
        if self.is_loaded(source):
            return

        try:
            module = importlib.import_module(source)
            # module inspection and loading logic here
            assert module
            self._mark_loaded(source)
        except Exception as exc:
            msg = f"Failed to load module {source}"
            raise LoaderError(msg) from exc
