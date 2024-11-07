# toolreg/registry/registration.py
"""Core registration functionality."""

from __future__ import annotations

import functools
import logging
from typing import TYPE_CHECKING, Any, TypeVar

from toolreg.registry import registry, tool


if TYPE_CHECKING:
    from collections.abc import Callable

    from toolreg import Example


logger = logging.getLogger(__name__)
T = TypeVar("T")


class ToolRegistrar:
    """Manages tool registration.

    This class handles registering tools with associated metadata. It provides
    a clean interface for both decorator-based and direct registration.
    """

    def __init__(self) -> None:
        """Initialize the registrar with a registry instance."""
        self._registry = registry.ToolRegistry()

    def register(
        self,
        func: Callable[..., Any],
        *,
        typ: registry.ItemType,
        name: str | None = None,
        group: str = "general",
        examples: list[Example] | None = None,
        required_packages: list[str] | None = None,
        aliases: list[str] | None = None,
        icon: str | None = None,
        description: str | None = None,
    ) -> None:
        """Register a function as a tool with metadata.

        Args:
            func: The function to register
            typ: Type of tool (filter, test, function)
            name: Optional override for function name
            group: Group/category for the tool
            examples: List of usage examples
            required_packages: Required package names
            aliases: Alternative names for the tool
            icon: Icon identifier
            description: Optional override for function description

        Raises:
            ValueError: If validation of the function or metadata fails
            RuntimeError: If registration fails
        """
        try:
            metadata = tool.Tool.from_function(
                func=func,
                typ=typ,
                name=name,
                group=group,
                examples=examples,
                required_packages=required_packages,
                aliases=aliases,
                icon=icon,
                description=description,
            )
        except Exception as exc:
            msg = f"Failed to create metadata for {func.__name__}"
            logger.exception(msg)
            raise ValueError(msg) from exc

        try:
            self._registry.register(func, metadata)
            logger.info("Registered %s as %s", func.__name__, typ)
        except Exception as exc:
            msg = f"Failed to register {func.__name__}"
            raise RuntimeError(msg) from exc


# Global registrar instance
_registrar = ToolRegistrar()


def register_tool(
    typ: registry.ItemType,
    *,
    name: str | None = None,
    group: str = "general",
    examples: list[Example] | None = None,
    required_packages: list[str] | None = None,
    aliases: list[str] | None = None,
    icon: str | None = None,
    description: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to register a function as a tool.

    Args:
        typ: Type of tool (filter, test, function)
        name: Optional override for function name
        group: Group/category for the tool
        examples: List of usage examples
        required_packages: Required package names
        aliases: Alternative names for the tool
        icon: Icon identifier
        description: Optional override for function description

    Returns:
        Decorator function that preserves the original function while registering it

    Example:
        ```python
        @register_tool(
            typ="filter",
            group="text",
            examples=[
                Example(
                    template="{{ 'hello' | uppercase }}",
                    title="Basic Example",
                )
            ],
            icon="mdi:format-letter-case-upper"
        )
        def uppercase(value: str) -> str:
            '''Convert string to uppercase.'''
            return value.upper()
        ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        _registrar.register(
            func,
            typ=typ,
            name=name,
            group=group,
            examples=examples,
            required_packages=required_packages,
            aliases=aliases,
            icon=icon,
            description=description,
        )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator
