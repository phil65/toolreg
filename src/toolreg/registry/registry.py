# toolreg/registry.py
from __future__ import annotations

from collections.abc import Callable
import functools
import inspect
import logging
import tomllib
from typing import Any, ClassVar, Literal, Self

from pydantic import BaseModel, Field
from upath import UPath


type FilterFunc = Callable[..., Any]
ItemType = Literal["filter", "test", "function"]


class Example(BaseModel):
    """Example for a jinja item."""

    template: str = Field(description="Template to render")
    description: str | None = Field(default=None, description="Example description")


class ToolMetadata(BaseModel):
    """Metadata for a jinja item."""

    name: str = Field(description="Name of the item")
    typ: ItemType = Field(description="Type of item (filter, test, function)")
    fn: str = Field(description="Import path for the function")
    group: str = Field(default="general", description="Group/category for organization")
    examples: dict[str, Example] = Field(
        default_factory=dict, description="Named usage examples"
    )
    required_packages: list[str] = Field(
        default_factory=list, description="Required Python packages"
    )
    aliases: list[str] = Field(default_factory=list, description="Alternative names")
    icon: str | None = Field(default=None, description="Icon identifier (e.g. mdi:home)")
    description: str | None = Field(default=None, description="Item description")

    @classmethod
    def from_function(cls, func: FilterFunc, typ: ItemType, **kwargs: Any) -> Self:
        """Create metadata from a function's attributes."""
        doc = inspect.getdoc(func) or ""

        return cls(
            name=kwargs.get("name", func.__name__),
            typ=typ,
            fn=f"{func.__module__}.{func.__name__}",
            description=kwargs.get("description", doc),
            **kwargs,
        )


class JinjaRegistry:
    """Singleton registry for jinja items."""

    _instance: ClassVar[JinjaRegistry | None] = None

    def __new__(cls) -> JinjaRegistry:  # noqa: PYI034
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._items: dict[str, tuple[FilterFunc, ToolMetadata]] = {}
            self._paths: set[UPath] = set()
            self._initialized = True

    def register(self, func: FilterFunc, metadata: ToolMetadata) -> None:
        """Register a new item with metadata."""
        self._items[metadata.name] = (func, metadata)
        for alias in metadata.aliases:
            self._items[alias] = (func, metadata)

    def get_all(
        self, typ: ItemType | None = None
    ) -> dict[str, tuple[FilterFunc, ToolMetadata]]:
        """Get all registered items, optionally filtered by type."""
        if typ is None:
            return self._items
        return {
            name: (func, meta)
            for name, (func, meta) in self._items.items()
            if meta.typ == typ
        }

    def load_path(self, path: str | UPath) -> None:
        """Load filters from a path (file or directory).

        Args:
            path: Path to TOML file or directory containing TOML files
        """
        path = UPath(path)
        if path in self._paths:
            return

        self._paths.add(path)

        if path.is_dir():
            for toml_file in path.glob("**/*.toml"):
                self._load_toml_file(toml_file)
        else:
            self._load_toml_file(path)

    def _load_toml_file(self, path: UPath) -> None:
        """Load filters from a TOML file.

        Args:
            path: Path to TOML file
        """
        try:
            content = path.read_text()
            data = tomllib.loads(content)

            # Process filters
            for name, item_data in data.get("filters", {}).items():
                try:
                    metadata = ToolMetadata.model_validate({
                        "name": name,
                        "typ": "filter",
                        **item_data,
                    })
                    func = self._import_function(metadata.fn)
                    self.register(func, metadata)
                except (ImportError, ValueError, TypeError):
                    logging.exception("Failed to load filter %s from %s", name, path)

            # Process tests
            for name, item_data in data.get("tests", {}).items():
                try:
                    metadata = ToolMetadata.model_validate({
                        "name": name,
                        "typ": "test",
                        **item_data,
                    })
                    func = self._import_function(metadata.fn)
                    self.register(func, metadata)
                except Exception:
                    logging.exception("Failed to load test %s", name)

            # Process functions
            for name, item_data in data.get("functions", {}).items():
                try:
                    metadata = ToolMetadata.model_validate({
                        "name": name,
                        "typ": "function",
                        **item_data,
                    })
                    func = self._import_function(metadata.fn)
                    self.register(func, metadata)
                except Exception:
                    logging.exception("Failed to load function %s from %s", name, path)

        except Exception:
            logging.exception("Failed to load file %s", path)

    def _validate_callable(self, obj: Any, import_path: str) -> None:
        """Validate that an imported object is callable.

        Args:
            obj: The object to validate
            import_path: The import path for error messages

        Raises:
            TypeError: If the object is not callable
        """
        if not callable(obj):
            msg = f"{import_path} is not callable"
            raise TypeError(msg)

    def _import_function(self, import_path: str) -> FilterFunc:
        """Import a function, method, or static method from its string path.

        Args:
            import_path: Import path in one of these formats:
                - builtin_function (e.g. 'repr', 'len')
                - module.function
                - module.Class.method
                - module.Class.staticmethod
                - module.submodule.function

        Returns:
            The imported callable

        Raises:
            ImportError: If the function cannot be imported or is not callable
        """
        # Handle built-in functions
        if "." not in import_path:
            try:
                obj = __builtins__[import_path]  # type: ignore
                if callable(obj):
                    return obj
                msg = f"{import_path} is not callable"
                raise ImportError(msg)
            except (KeyError, TypeError) as e:
                msg = f"Built-in {import_path} not found"
                raise ImportError(msg) from e

        try:
            parts = import_path.split(".")
            module_path = ".".join(parts[:-2] if len(parts) > 2 else parts[:-1])  # noqa: PLR2004
            attr_path = parts[-2:] if len(parts) > 2 else parts[-1:]  # noqa: PLR2004

            module = __import__(module_path, fromlist=attr_path)
            obj = module

            for attr in attr_path:
                obj = getattr(obj, attr)

                # If this is a method descriptor (classmethod/staticmethod), get the func
                if hasattr(obj, "__func__"):
                    obj = obj.__func__

            self._validate_callable(obj, import_path)

        except Exception as e:
            msg = f"Failed to import function {import_path}"
            raise ImportError(msg) from e
        else:
            return obj


def register_jinjaitem(
    typ: ItemType,
    *,
    name: str | None = None,
    group: str = "general",
    examples: dict[str, dict[str, str]] | None = None,
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
        examples: Dict of named examples
        required_packages: Required package names
        aliases: Alternative names for the item
        icon: Icon identifier
        **kwargs: Additional metadata

    Example:
        ```python
        @register_jinjaitem(
            typ="filter",
            group="text",
            examples={
                "basic": {
                    "template": "{{ 'hello' | uppercase }}",
                    "description": "Basic example"
                }
            },
            icon="mdi:format-letter-case-upper"
        )
        def uppercase(value: str) -> str:
            '''Convert string to uppercase.'''
            return value.upper()
        ```
    """

    def decorator(func: FilterFunc) -> FilterFunc:
        registry = JinjaRegistry()

        example_objects = {}
        if examples:
            example_objects = {
                name: Example.model_validate(ex) for name, ex in examples.items()
            }

        metadata_kwargs = {
            "typ": typ,
            "group": group,
            "examples": example_objects,
            "required_packages": required_packages or [],
            "aliases": aliases or [],
            "icon": icon,
        }
        if name is not None:
            metadata_kwargs["name"] = name

        metadata = ToolMetadata.from_function(
            func,
            **metadata_kwargs,  # type: ignore[arg-type]
            **kwargs,
        )
        registry.register(func, metadata)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    import jinja2

    # Load from TOML files
    registry = JinjaRegistry()
    registry.load_path("src/toolreg/resources/")  # Load all TOML files
    registry.load_path("src/toolreg/resources/filters.toml")  # Load single file

    # Using the decorator
    @register_jinjaitem(
        typ="filter",
        group="text",
        examples={
            "basic": {
                "template": "{{ 'hello' | uppercase }}",
                "description": "Basic example",
            }
        },
    )
    def uppercase(value: str) -> str:
        """Convert string to uppercase."""
        return value.upper()

    # Environment integration remains the same
    class Environment(jinja2.Environment):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)

            registry = JinjaRegistry()
            for name, (func, _metadata) in registry.get_all(typ="filter").items():
                self.filters[name] = func

    env = Environment()
    print(env.filters.keys())
