# toolreg/registry/registry.py
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal

from toolreg.registry.register_tool import register_tool


type FilterFunc = Callable[..., Any]
ItemType = Literal["filter", "test", "function"]


if TYPE_CHECKING:
    from toolreg.registry import tool


class JinjaRegistry:
    """Singleton registry for jinja items."""

    _instance: JinjaRegistry | None = None

    def __new__(cls) -> JinjaRegistry:  # noqa: PYI034
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_items"):
            self._items: dict[str, tuple[FilterFunc, tool.ToolMetadata]] = {}

    def register(self, func: FilterFunc, metadata: tool.ToolMetadata) -> None:
        """Register a new item with metadata."""
        self._items[metadata.name] = (func, metadata)
        # Also register aliases
        for alias in metadata.aliases:
            self._items[alias] = (func, metadata)

    def get_all(
        self,
        typ: ItemType | None = None,
    ) -> dict[str, tuple[FilterFunc, tool.ToolMetadata]]:
        """Get all registered items, optionally filtered by type."""
        if typ is None:
            return self._items
        return {
            name: (func, meta)
            for name, (func, meta) in self._items.items()
            if meta.typ == typ
        }


if __name__ == "__main__":
    # Example 1: Basic filter with docstring-based metadata
    @register_tool(typ="filter", group="text")
    def uppercase(value: str) -> str:
        """Convert string to uppercase.

        Examples:
            >>> uppercase('hello')
            'HELLO'

            >>> uppercase('Hello World')
            'HELLO WORLD'
        """
        return value.upper()
