"""Tool registration functionality."""

from __future__ import annotations

import functools
import logging
from typing import TYPE_CHECKING, Any

from toolreg.registry import registry, tool


if TYPE_CHECKING:
    from collections.abc import Callable

    from toolreg.registry.example import Example
    from toolreg.registry.registry import FilterFunc, ItemType


class ToolRegistrar:
    """Manages tool registration.

    This class handles registering tools with associated metadata. It provides
    a clean interface for both decorator-based and direct registration.

    Example:
        ```python
        # Direct registration
        registrar = ToolRegistrar()
        registrar.load_fn(my_func, typ="filter", group="text")

        # Or via decorator
        @register_tool(typ="filter", group="text")
        def my_func(): ...
        ```
    """

    def __init__(self) -> None:
        """Initialize the registrar with a registry instance."""
        self._registry = registry.ToolRegistry()

    def load_fn(
        self,
        func: Callable[..., Any],
        *,
        typ: ItemType,
        name: str | None = None,
        group: str = "general",
        examples: list[Example] | None = None,
        required_packages: list[str] | None = None,
        aliases: list[str] | None = None,
        icon: str | None = None,
        description: str | None = None,
    ) -> None:
        """Load and register a function as a tool.

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
        except Exception as e:
            msg = f"Failed to create metadata for {func.__name__}"
            logging.exception(msg)
            raise ValueError(msg) from e

        try:
            self._registry.register(func, metadata)
        except Exception as e:
            msg = f"Failed to register {func.__name__}"
            raise RuntimeError(msg) from e


def register_tool(
    typ: ItemType,
    *,
    name: str | None = None,
    group: str = "general",
    examples: list[Example] | None = None,
    required_packages: list[str] | None = None,
    aliases: list[str] | None = None,
    icon: str | None = None,
    description: str | None = None,
) -> Callable[[FilterFunc], FilterFunc]:
    """Decorator to register a function as a tool.

    This decorator uses ToolRegistrar to handle the actual registration process.

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

    def decorator(func: FilterFunc) -> FilterFunc:
        registrar = ToolRegistrar()
        registrar.load_fn(
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


if __name__ == "__main__":
    import jinja2

    from toolreg.registry import example, registry, tool

    # Example using decorator
    @register_tool(
        typ="filter",
        group="text",
        examples=[
            example.Example(
                template="{{ 'hello' | upper }}",
                title="Basic Example",
                description="Basic uppercase example",
            )
        ],
        icon="mdi:format-letter-case-upper",
    )
    def uppercase(value: str) -> str:
        """Convert string to uppercase.

        Args:
            value: Input string

        Returns:
            Uppercase string
        """
        return value.upper()

    # Example using direct registration
    def lowercase(value: str) -> str:
        """Convert string to lowercase."""
        return value.lower()

    registrar = ToolRegistrar()
    registrar.load_fn(
        lowercase,
        typ="filter",
        group="text",
        icon="mdi:format-letter-case-lower",
    )

    # Test with Environment
    class Environment(jinja2.Environment):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)

            reg = registry.ToolRegistry()
            for name, (func, _metadata) in reg.get_all(typ="filter").items():
                self.filters[name] = func

    env = Environment()
    print(env.filters)
