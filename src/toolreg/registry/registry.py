from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal


if TYPE_CHECKING:
    from toolreg.registry import tool


type FilterFunc = Callable[..., Any]
type ItemType = Literal["filter", "test", "function"]


class ToolRegistry:
    """Registry for jinja items."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._items: dict[str, tuple[FilterFunc, tool.Tool]] = {}

    def register(self, func: FilterFunc, metadata: tool.Tool) -> None:
        """Register a new item with metadata."""
        self._items[metadata.name] = (func, metadata)
        # Also register aliases
        for alias in metadata.aliases:
            self._items[alias] = (func, metadata)

    def get_all(
        self,
        typ: ItemType | None = None,
    ) -> dict[str, tuple[FilterFunc, tool.Tool]]:
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
    from toolreg import register_tool

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
