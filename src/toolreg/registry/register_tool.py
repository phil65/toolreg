"""Tool registration decorator."""

from __future__ import annotations

from collections.abc import Callable
import functools
from typing import Any, Literal


ItemType = Literal["filter", "test", "function"]
FilterFunc = Callable[..., Any]


def register_tool(
    typ: ItemType,
    *,
    name: str | None = None,
    group: str = "general",
    examples: example.ExampleList | None = None,
    required_packages: list[str] | None = None,
    aliases: list[str] | None = None,
    icon: str | None = None,
    description: str | None = None,
) -> Callable[[FilterFunc], FilterFunc]:
    """Decorator to register a jinja item.

    Args:
        typ: Type of item (filter, test, function)
        name: Optional name override
        group: Group/category for the item
        examples: Dictionary of examples
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
                    content="{{ 'hello' | uppercase }}",
                    title="Basic Example",
                    description="Simple uppercase example"
                )
            ],
            icon="mdi:format-letter-case-upper"
        )
        def uppercase(value: str) -> str:
            '''Convert string to uppercase.'''
            return value.upper()
        ```

    Returns:
        Decorated function
    """

    def decorator(func: FilterFunc) -> FilterFunc:
        from toolreg.registry import registry, tool

        reg_instance = registry.ToolRegistry()

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
        reg_instance.register(func, metadata)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    import jinja2

    from toolreg.registry import example

    @register_tool(
        typ="filter",
        group="text",
        examples=[
            example.Example(
                template="{{ 'hello' | upper }}",
                title="Basic Example",
                description="Basic uppercase example",
                markdown=False,
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
