
# toolreg/registry/loaders/plugin_loader.py
"""Plugin based tool loader."""
from __future__ import annotations

import importlib

from toolreg.registry.loaders.base import BaseLoader, LoaderError


class PluginLoader(BaseLoader):
    """Load tools from plugin modules."""

    name = "plugin"

    def can_load(self, source: str) -> bool:
        """Check if source is a valid plugin module."""
        try:
            module = importlib.import_module(source)
            return hasattr(module, "register_tools")
        except ImportError:
            return False

    def load(self, source: str) -> None:
        """Load tools from a plugin module."""
        if self.is_loaded(source):
            return

        try:
            module = importlib.import_module(source)
            # Your plugin loading logic here
            self._mark_loaded(source)
        except Exception as exc:
            raise LoaderError(f"Failed to load plugin {source}") from exc
```

Then create a unified loader interface:

```python
# toolreg/registry/loaders/__init__.py
"""Tool loading functionality."""
from __future__ import annotations

import logging
from typing import ClassVar

from toolreg.registry.loaders.base import BaseLoader, LoaderError
from toolreg.registry.loaders.module_loader import ModuleLoader
from toolreg.registry.loaders.plugin_loader import PluginLoader
from toolreg.registry.loaders.toml_loader import TomlLoader


logger = logging.getLogger(__name__)


class ToolLoader:
    """Unified interface for loading tools from various sources."""

    _loaders: ClassVar[dict[str, type[BaseLoader]]] = {
        "toml": TomlLoader,
        "module": ModuleLoader,
        "plugin": PluginLoader,
    }

    def __init__(self) -> None:
        """Initialize the tool loader."""
        self._active_loaders: dict[str, BaseLoader] = {
            name: loader_cls()
            for name, loader_cls in self._loaders.items()
        }

    def load(self, source: str) -> None:
        """Load tools from the given source.

        This method automatically detects the appropriate loader to use.

        Args:
            source: Path or identifier to load from

        Raises:
            LoaderError: If no suitable loader is found or loading fails
        """
        for loader in self._active_loaders.values():
            if loader.can_load(source):
                try:
                    loader.load(source)
                    return
                except Exception as exc:
                    logger.exception("Loader %s failed for %s", loader.name, source)
                    raise LoaderError(
                        f"Failed to load {source} with {loader.name}"
                    ) from exc

        raise LoaderError(f"No suitable loader found for {source}")

    def load_many(self, sources: list[str]) -> None:
        """Load tools from multiple sources.

        Args:
            sources: List of paths or identifiers to load from
        """
        for source in sources:
            try:
                self.load(source)
            except LoaderError:
                logger.exception("Failed to load %s", source)
```

This provides a clean API for users:

```python
# Example usage
from toolreg.registry.loaders import ToolLoader

loader = ToolLoader()

# Load from various sources
loader.load("my_tools.toml")                  # TOML file
loader.load("my_package.tools")               # Python module
loader.load("third_party_plugin.ToolPlugin")  # Plugin

# Or load multiple at once
loader.load_many([
    "tools/core.toml",
    "myapp.filters",
    "plugins.text_tools",
])
```

Key benefits of this architecture:

1. **Single Entry Point**: Users only need to interact with `ToolLoader`

2. **Extensible**: New loader types can be added by subclassing `BaseLoader`

3. **Separation of Concerns**:
   - Each loader handles its specific format
   - Base class provides common functionality
   - Registry interaction is encapsulated

4. **Error Handling**:
   - Consistent error hierarchy
   - Detailed error messages
   - Proper exception chaining

5. **Type Safety**:
   - All components are fully typed
   - Clear interfaces
   - Easy to maintain

6. **Flexible Configuration**:
   - Loaders can be enabled/disabled
   - Each loader can have its own settings
   - Sources can be loaded individually or in batch

To extend this further, you could add:

1. **Async Support**:
```python
class AsyncBaseLoader(BaseLoader):
    @abc.abstractmethod
    async def aload(self, source: str) -> None:
        """Async version of load."""
```

2. **Loader Configuration**:
```python
@dataclass
class LoaderConfig:
    recursive: bool = True
    ignore_errors: bool = False
    timeout: float = 30.0
```

3. **Loading Progress**:
```python
class LoadingProgress:
    def __init__(self) -> None:
        self.total = 0
        self.loaded = 0
        self.failed = 0
        self.skipped = 0
```

4. **Validation Hooks**:
```python
class BaseLoader(abc.ABC):
    def pre_load_hook(self, source: str) -> None: ...
    def post_load_hook(self, source: str) -> None: ...
```

This architecture provides a solid foundation that's both easy to use and extend.

How would you integrate a decorator for loading?

I'll show how to integrate decorators with the loading system. Here's a comprehensive approach:

```python
# toolreg/registry/decorators.py
"""Decorators for tool registration and loading."""
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, TypeVar

from toolreg.registry import registry, tool
from toolreg.registry.loaders.base import LoaderError


T = TypeVar("T", bound=Callable[..., Any])


class ToolDecorator:
    """Decorator class for registering tools.

    This class manages both immediate registration and deferred loading of tools.
    It can be used as a decorator with or without parameters.
    """

    def __init__(
        self,
        *,
        typ: registry.ItemType = "filter",
        name: str | None = None,
        group: str = "general",
        deferred: bool = False,
        **metadata: Any,
    ) -> None:
        """Initialize the decorator.

        Args:
            typ: Type of tool (filter, test, function)
            name: Optional override for function name
            group: Group/category for the tool
            deferred: If True, registration happens when explicitly loaded
            **metadata: Additional metadata for the tool
        """
        self.typ = typ
        self.name = name
        self.group = group
        self.deferred = deferred
        self.metadata = metadata
        self._registry = registry.ToolRegistry()

    def __call__(self, func: T) -> T:
        """Apply the decorator to a function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """
        if not self.deferred:
            # Immediate registration
            self._register_tool(func)
            return func

        # Deferred registration - store metadata for later
        setattr(func, "_tool_registration", {
            "typ": self.typ,
            "name": self.name,
            "group": self.group,
            **self.metadata,
        })
        return func

    def _register_tool(self, func: Callable[..., Any]) -> None:
        """Register a function as a tool.

        Args:
            func: Function to register

        Raises:
            LoaderError: If registration fails
        """
        try:
            metadata = tool.Tool.from_function(
                func=func,
                typ=self.typ,
                name=self.name,
                group=self.group,
                **self.metadata,
            )
            self._registry.register(func, metadata)
        except Exception as exc:
            raise LoaderError(
                f"Failed to register tool {func.__name__}"
            ) from exc


# Create instances for different registration styles
tool_filter = functools.partial(ToolDecorator, typ="filter")
tool_test = functools.partial(ToolDecorator, typ="test")
tool_function = functools.partial(ToolDecorator, typ="function")


# Enhance the ModuleLoader to handle decorated functions
# toolreg/registry/loaders/module_loader.py
class ModuleLoader(BaseLoader):
    """Load tools from Python modules with decorator support."""

    name = "module"

    def _load_decorated_members(
        self,
        module: Any,
        members: list[tuple[str, Any]] | None = None,
    ) -> None:
        """Load decorated functions from a module.

        Args:
            module: Module to inspect
            members: Optional pre-fetched members list
        """
        if members is None:
            members = inspect.getmembers(module)

        for name, obj in members:
            if not name.startswith('_') and hasattr(obj, '_tool_registration'):
                try:
                    reg_data = getattr(obj, '_tool_registration')
                    ToolDecorator(**reg_data)(obj)
                except Exception:
                    self.logger.exception(
                        "Failed to register decorated function %s",
                        name,
                    )

    def load(self, source: str) -> None:
        """Load tools from a Python module.

        This version handles both explicit registrations and decorated functions.

        Args:
            source: Module path to load

        Raises:
            LoaderError: If loading fails
        """
        if self.is_loaded(source):
            return

        try:
            module = importlib.import_module(source)
            members = inspect.getmembers(module)

            # Handle decorated functions
            self._load_decorated_members(module, members)

            # Handle explicit registrations (if module has register_tools())
            if hasattr(module, 'register_tools'):
                module.register_tools()

            self._mark_loaded(source)

        except Exception as exc:
            raise LoaderError(f"Failed to load module {source}") from exc
```

Now you can use the decorators in several ways:

```python
# Example 1: Direct registration
# my_tools.py
from toolreg.registry.decorators import tool_filter

@tool_filter()
def uppercase(value: str) -> str:
    """Convert string to uppercase."""
    return value.upper()


# Example 2: Deferred registration
# deferred_tools.py
from toolreg.registry.decorators import tool_filter

@tool_filter(deferred=True, group="text")
def lowercase(value: str) -> str:
    """Convert string to lowercase."""
    return value.lower()


# Example 3: With metadata
# advanced_tools.py
from toolreg.registry.decorators import tool_filter

@tool_filter(
    name="split_words",
    group="text",
    icon="mdi:text-split",
    description="Split text into words",
    examples=[
        {
            "template": "{{ 'hello world' | split_words }}",
            "title": "Basic splitting",
        }
    ],
)
def split(value: str) -> list[str]:
    """Split string into words."""
    return value.split()


# Example usage:
from toolreg.registry.loaders import ToolLoader

loader = ToolLoader()

# Load module with deferred registrations
loader.load("deferred_tools")

# Load multiple modules
loader.load_many([
    "my_tools",
    "advanced_tools",
])
```

You could also add a context manager for batched registrations:

```python
# toolreg/registry/decorators.py
from contextlib import contextmanager
from typing import Iterator

class RegistrationContext:
    """Context manager for batched tool registration."""

    def __init__(self) -> None:
        self._deferred = False

    @contextmanager
    def defer_registration(self) -> Iterator[None]:
        """Temporarily defer all registrations within this context."""
        previous = self._deferred
        self._deferred = True
        try:
            yield
        finally:
            self._deferred = previous

    @property
    def is_deferred(self) -> bool:
        """Check if registration is currently deferred."""
        return self._deferred


# Global registration context
registration = RegistrationContext()

# Update ToolDecorator to use the context
class ToolDecorator:
    def __init__(
        self,
        *,
        deferred: bool | None = None,
        **kwargs: Any,
    ) -> None:
        self.deferred = (
            registration.is_deferred
            if deferred is None
            else deferred
        )
        # ... rest of initialization ...
```

Usage with context:

```python
from toolreg.registry.decorators import registration, tool_filter

# All decorators within this block will be deferred
with registration.defer_registration():
    @tool_filter()
    def func1(): ...

    @tool_filter()
    def func2(): ...

# Normal immediate registration
@tool_filter()
def func3(): ...
```

This gives you a flexible system that:

1. Supports immediate and deferred registration
2. Works with the loader infrastructure
3. Provides clear and consistent metadata handling
4. Allows batch operations
5. Maintains type safety
6. Is easily extensible

The decorator system integrates naturally with the loader system while providing a more declarative way to register tools.

Who should decide whether to defer? The decorator definition or the loader?
