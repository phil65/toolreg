from __future__ import annotations

from collections.abc import Callable, Sequence
import functools
import inspect
from typing import TYPE_CHECKING, Any, Literal, Self

from pydantic import BaseModel, Field, ImportString


if TYPE_CHECKING:
    from toolreg.utils import slugfield


type FilterFunc = Callable[..., Any]
ItemType = Literal["filter", "test", "function"]


class Example(BaseModel):
    """Example model for jinja items."""

    content: str = Field(description="Template content to render")
    title: str = Field(description="Title of the example")
    description: str | None = Field(default=None, description="Example description")
    markdown: bool = Field(default=False, description="Whether content is markdown")


class ToolMetadata(BaseModel):
    """Metadata for a jinja item."""

    name: slugfield.Slug
    """ame of the jinja item"""
    typ: ItemType
    """ype of the item (filter, test, or function)"""
    import_path: ImportString[Callable[..., Any]]
    """mport path in the format "package.module.function"""
    description: str | None = None
    """ptional description of what the item does"""
    group: str = "general"
    """roup/category for organizing items"""
    examples: list[Example] = Field(default_factory=list)
    """ist of usage examples"""
    required_packages: list[str] = Field(default_factory=list)
    """ython packages required for this item"""
    aliases: list[str] = Field(default_factory=list)
    """lternative names that can be used to access this item"""
    icon: str | None = None
    """ptional icon identifier"""

    @classmethod
    def from_function(cls, func: FilterFunc, typ: ItemType, **kwargs: Any) -> Self:
        """Create metadata from a function's attributes.

        Args:
            func: Function to create metadata from
            typ: Type of jinja item
            **kwargs: Additional metadata

        Returns:
            New metadata instance

        Raises:
            ValueError: If function path cannot be determined
        """
        # Extract info from docstring
        doc = inspect.getdoc(func) or ""

        # Get required packages from docstring (could use regex)
        required: list[str] = []  # parse from docstring

        # Get the complete import path
        if inspect.ismethod(func):
            # Handle instance methods, class methods, and static methods
            if hasattr(func, "__self__"):
                if inspect.isclass(func.__self__):  # classmethod
                    qual_name = f"{func.__self__.__module__}.{func.__qualname__}"
                else:  # instance method
                    qual_name = (
                        f"{func.__self__.__class__.__module__}.{func.__qualname__}"
                    )
            else:  # static method
                qual_name = f"{func.__module__}.{func.__qualname__}"
        elif inspect.isfunction(func):
            # Regular function
            qual_name = f"{func.__module__}.{func.__qualname__}"
        # Built-in function or other callable
        elif hasattr(func, "__module__") and hasattr(func, "__qualname__"):
            qual_name = f"{func.__module__}.{func.__qualname__}"
        else:
            msg = f"Could not determine import path for {func}"
            raise ValueError(msg)

        return cls(
            name=kwargs.get("name", func.__name__),
            typ=typ,
            import_path=qual_name,
            description=kwargs.get("description", doc),
            required_packages=kwargs.get("required_packages", required),
            **kwargs,
        )


class JinjaRegistry:
    """Singleton registry for jinja items."""

    _instance: JinjaRegistry | None = None

    def __new__(cls) -> JinjaRegistry:  # noqa: PYI034
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_items"):
            self._items: dict[str, tuple[FilterFunc, ToolMetadata]] = {}

    def register(self, func: FilterFunc, metadata: ToolMetadata) -> None:
        """Register a new item with metadata."""
        self._items[metadata.name] = (func, metadata)
        # Also register aliases
        for alias in metadata.aliases:
            self._items[alias] = (func, metadata)

    def get_all(
        self,
        typ: ItemType | None = None,
    ) -> dict[str, tuple[FilterFunc, ToolMetadata]]:
        """Get all registered items, optionally filtered by type."""
        if typ is None:
            return self._items
        return {
            name: (func, meta)
            for name, (func, meta) in self._items.items()
            if meta.typ == typ
        }


def register_tool(
    typ: ItemType,
    *,
    name: str | None = None,
    group: str = "general",
    examples: Sequence[Example] | None = None,
    required_packages: list[str] | None = None,
    aliases: list[str] | None = None,
    icon: str | None = None,
    **kwargs: Any,
) -> Callable[[FilterFunc], FilterFunc]:
    """Decorator to register a jinja item.

    Args:
        typ: Type of item (filter, test, function)
        name: Optional name override
        group: Group/category for the item
        examples: Sequence of example models
        required_packages: Required package names
        aliases: Alternative names for the item
        icon: Icon identifier
        **kwargs: Additional metadata

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
        registry = JinjaRegistry()

        # Create base kwargs
        metadata_kwargs = {
            "group": group,
            "examples": list(examples) if examples else [],
            "aliases": aliases or [],
            "icon": icon,
        }

        # Only add name if explicitly provided
        if name is not None:
            metadata_kwargs["name"] = name
        if required_packages is not None:
            metadata_kwargs["required_packages"] = required_packages
        # Create metadata
        metadata = ToolMetadata.from_function(
            func,
            typ=typ,
            **metadata_kwargs,
            **kwargs,
        )

        # Register the function
        registry.register(func, metadata)

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
            Example(
                content="{{ 'hello' | uppercase }}",
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
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)

            # Load all registered filters
            registry = JinjaRegistry()
            for name, (func, _metadata) in registry.get_all(typ="filter").items():
                self.filters[name] = func

    env = Environment()
    print(env.filters)
