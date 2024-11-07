"""Base classes for tool loading mechanisms."""

from __future__ import annotations

import abc
import logging

from toolreg.registry import registry


logger = logging.getLogger(__name__)


class BaseLoader(abc.ABC):
    """Abstract base class for all tool loaders."""

    name: str
    """Identifier for the loader type"""

    def __init__(self, registry_instance: registry.ToolRegistry | None = None) -> None:
        """Initialize the loader with a registry reference.

        Args:
            registry_instance: The registry to register tools in
        """
        self._registry = registry_instance or registry.ToolRegistry()
        self._loaded_items: set[str] = set()

    @abc.abstractmethod
    def can_load(self, source: str) -> bool:
        """Check if this loader can handle the given source."""

    @abc.abstractmethod
    def load(self, source: str, *, recursive: bool = True) -> None:
        """Load tools from the given source."""

    def _mark_loaded(self, identifier: str) -> None:
        """Mark a source as loaded."""
        self._loaded_items.add(identifier)

    def is_loaded(self, identifier: str) -> bool:
        """Check if a source has already been loaded."""
        return identifier in self._loaded_items


class LoaderError(Exception):
    """Base exception for loader errors."""
