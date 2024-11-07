"""Python module based tool loader."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
from typing import TYPE_CHECKING, Any, Literal

from toolreg.registry import tool
from toolreg.registry.loaders.base import BaseLoader, LoaderError
from toolreg.utils import package_utils


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    Tool = Callable[..., Any]


def is_tool(obj: Any) -> bool:
    """Check if an object is a potential tool.

    Args:
        obj: Object to check

    Returns:
        True if object appears to be a tool
    """
    return callable(obj) and not obj.__name__.startswith("_") and inspect.isfunction(obj)


def iter_tools(module: Any) -> Iterator[tuple[str, Tool]]:
    """Find all tool functions in a module.

    Args:
        module: Module object to inspect

    Yields:
        Tuples of (name, function) for each tool found
    """
    for name, obj in inspect.getmembers(module):
        if is_tool(obj):
            yield name, obj


class ModuleLoader(BaseLoader):
    """Load tools from Python modules."""

    name = "module"

    def can_load(self, source: str) -> bool:
        """Check if source is a valid Python module path."""
        try:
            return bool(importlib.util.find_spec(source))
        except ModuleNotFoundError:
            return False

    def load(
        self,
        source: str,
        *,
        required_packages: list[str] | None = None,
        typ: Literal["filter", "test", "function"] = "filter",
        group: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Load tools from a Python module.

        Args:
            source: Module path to load
            required_packages: Optional list of required packages.
                If not provided, will try to auto-detect from module path.
            typ: Type of tools to register ("filter", "test", "function")
            group: Optional group name for the tools
            **kwargs: Additional loader arguments

        Raises:
            LoaderError: If loading fails
        """
        if self.is_loaded(source):
            return

        try:
            module = importlib.import_module(source)

            # Get package name if not explicitly provided
            if required_packages is None:
                if package := package_utils.get_package_name(source):
                    required_packages = [package]
                else:
                    required_packages = []

            # Inspect module for tools
            for name, func in iter_tools(module):
                try:
                    metadata = tool.Tool.from_function(
                        func,
                        typ=typ,
                        group=group,
                        required_packages=required_packages,
                    )
                    self._registry.register(func, metadata)
                    logger.debug("Registered tool %r from %s", name, source)
                except Exception:
                    logger.exception(
                        "Failed to register tool %r from %s",
                        name,
                        source,
                    )

            self._mark_loaded(source)

        except Exception as exc:
            msg = f"Failed to load module {source}"
            raise LoaderError(msg) from exc
