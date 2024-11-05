from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, ClassVar

from toolreg.registry import example, registry, tool


if TYPE_CHECKING:
    from collections.abc import Callable


class ToolRegistrar:
    """Manages tool registration with deferred processing."""

    _instance: ClassVar[ToolRegistrar | None] = None
    _pending_registrations: list[tuple[Callable[..., Any], dict[str, Any]]]

    def __new__(cls) -> ToolRegistrar:  # noqa: PYI034
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_pending_registrations"):
            self._pending_registrations = []

    def add_pending(
        self,
        func: Callable[..., Any],
        metadata_kwargs: dict[str, Any],
    ) -> None:
        """Queue a function for later registration."""
        self._pending_registrations.append((func, metadata_kwargs))

    def process_pending(self) -> None:
        """Process all pending registrations.

        This method creates the metadata and registers all pending tools with the
        ToolRegistry.
        """
        reg = registry.ToolRegistry()

        for func, metadata_kwargs in self._pending_registrations:
            try:
                metadata = tool.Tool.from_function(func=func, **metadata_kwargs)
                reg.register(func, metadata)
            except Exception as e:
                # Log error but continue processing other registrations
                msg = f"Failed to register {func.__name__}: {e}"
                raise RuntimeError(msg) from e

        # Clear processed registrations
        self._pending_registrations.clear()


def register_tool(
    typ: registry.ItemType,
    *,
    name: str | None = None,
    group: str = "general",
    examples: list[example.Example] | None = None,
    required_packages: list[str] | None = None,
    aliases: list[str] | None = None,
    icon: str | None = None,
    description: str | None = None,
) -> Callable[[registry.FilterFunc], registry.FilterFunc]:
    """Decorator to queue a tool for registration.

    Instead of immediately processing and registering the tool, this decorator
    queues the function for later registration. The actual registration happens
    when ToolRegistrar.process_pending() is called.

    Args:
        typ: Type of item (filter, test, function)
        name: Optional name override
        group: Group/category for the item
        examples: List of usage examples
        required_packages: Required package names
        aliases: Alternative names for the item
        icon: Icon identifier
        description: Optional override for function description

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

        # Later, when ready to process:
        ToolRegistrar().process_pending()
        ```

    Returns:
        Decorated function
    """

    def decorator(func: registry.FilterFunc) -> registry.FilterFunc:
        # Store metadata args for later processing
        metadata_kwargs = {
            "typ": typ,
            "name": name,
            "group": group,
            "examples": examples,
            "required_packages": required_packages,
            "aliases": aliases,
            "icon": icon,
            "description": description,
        }

        registrar = ToolRegistrar()
        registrar.add_pending(func, metadata_kwargs)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    import jinja2

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

    # Test with a class method and static method
    class TestClass:
        @classmethod
        @register_tool(typ="filter", group="test")
        def class_method(cls, value: str) -> str:
            """Test class method."""
            return value

        @staticmethod
        @register_tool(typ="filter", group="test")
        def static_method(value: str) -> str:
            """Test static method."""
            return value

    # Process all pending registrations
    ToolRegistrar().process_pending()

    # Environment integration
    class Environment(jinja2.Environment):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)

            # Load all registered filters
            reg = registry.ToolRegistry()
            for name, (func, _metadata) in reg.get_all(typ="filter").items():
                self.filters[name] = func

    env = Environment()
    print(env.filters)
