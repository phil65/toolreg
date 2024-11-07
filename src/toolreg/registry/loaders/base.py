"""Base classes for tool loading mechanisms."""

from __future__ import annotations

import abc
import logging
from typing import ClassVar

from toolreg.registry import registry


logger = logging.getLogger(__name__)


class BaseLoader(abc.ABC):
    """Abstract base class for all tool loaders."""

    name: ClassVar[str]
    """Identifier for the loader type"""

    def __init__(self) -> None:
        """Initialize the loader with a registry reference."""
        self._registry = registry.ToolRegistry()
        self._loaded_items: set[str] = set()

    @abc.abstractmethod
    def can_load(self, source: str) -> bool:
        """Check if this loader can handle the given source.

        Args:
            source: Path or identifier to check

        Returns:
            True if this loader can handle the source
        """

    @abc.abstractmethod
    def load(self, source: str) -> None:
        """Load tools from the given source.

        Args:
            source: Path or identifier to load from

        Raises:
            LoaderError: If loading fails
        """

    def _mark_loaded(self, identifier: str) -> None:
        """Mark a source as loaded.

        Args:
            identifier: Unique identifier for the loaded source
        """
        self._loaded_items.add(identifier)

    def is_loaded(self, identifier: str) -> bool:
        """Check if a source has already been loaded.

        Args:
            identifier: Source identifier to check

        Returns:
            True if already loaded
        """
        return identifier in self._loaded_items


class LoaderError(Exception):
    """Base exception for loader errors."""
