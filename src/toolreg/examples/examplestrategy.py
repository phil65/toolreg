from __future__ import annotations

from abc import ABC, abstractmethod
import datetime as dt
import decimal
import enum
import inspect
import ipaddress
import pathlib
import re
import typing
from typing import Any
import uuid


if typing.TYPE_CHECKING:
    from toolreg.registry.tool import Tool


class ExampleStrategy(ABC):
    """Abstract base class for example generation strategies."""

    @abstractmethod
    def generate(self, tool: Tool) -> str:
        """Generate an example string for the given tool.

        Args:
            tool: The tool to generate an example for

        Returns:
            Generated example string
        """
        return NotImplemented


class FilterExampleStrategy(ExampleStrategy):
    """Strategy for generating filter examples."""

    def __init__(self) -> None:
        """Initialize the type mapping for example values."""
        super().__init__()
        self.type_mapping: dict[type, Any] = {
            str: "Hello, World!",
            int: 42,
            float: 3.14159,
            bool: True,
            bytes: b"example",
            bytearray: bytearray(b"example"),
            complex: 1 + 2j,
            frozenset: frozenset([1, 2, 3]),
            range: range(3),
            memoryview: memoryview(b"example"),
            object: object(),
            dt.date: dt.date(2024, 1, 1),
            dt.time: dt.time(12, 0),
            dt.datetime: dt.datetime(2024, 1, 1, 12, 0),
            dt.timedelta: dt.timedelta(days=1),
            uuid.UUID: uuid.uuid4(),
            ipaddress.IPv4Address: ipaddress.IPv4Address("192.0.2.1"),
            ipaddress.IPv6Address: ipaddress.IPv6Address("2001:db8::1"),
            list: [1, 2, 3],
            dict: {"key": "value"},
            set: {1, 2, 3},
            tuple: (1, 2, 3),
            pathlib.Path: pathlib.Path("/tmp/example"),
            decimal.Decimal: decimal.Decimal("3.14"),
            enum.Enum: enum.Enum("Color", "RED GREEN BLUE"),
            re.Pattern: re.compile(r"\w+"),
        }

    def get_example_value(self, type_hint: Any) -> Any:  # noqa: PLR0911
        """Generate a realistic example value based on a type hint.

        Args:
            type_hint: The type hint to generate an example for

        Returns:
            An appropriate example value for the given type
        """
        if type_hint in (inspect.Parameter.empty, Any):
            return "example_text"

        # Handle Optional/Union types
        origin = typing.get_origin(type_hint)
        if origin is not None:
            args = typing.get_args(type_hint)
            if origin == typing.Union:
                # For Optional/Union types, use the first non-None type
                return next(
                    (
                        self.get_example_value(arg)
                        for arg in args
                        if arg is not type(None)
                    ),
                    "example_text",
                )
            if origin in (list, list):
                return [self.get_example_value(args[0])] if args else [1, 2, 3]
            if origin in (dict, dict):
                key_type = args[0] if args else str
                value_type = args[1] if len(args) > 1 else Any
                return {
                    self.get_example_value(key_type): self.get_example_value(value_type)
                }

        if value := self.type_mapping.get(type_hint):
            return value

        # For unknown types, return a string representation
        try:
            return f"example_{type_hint.__name__.lower()}"
        except AttributeError:
            return "example_unknown"

    def format_value(self, value: Any) -> str:
        """Format a value for use in a template.

        Args:
            value: The value to format

        Returns:
            Formatted string representation of the value
        """
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, dt.datetime | dt.date):
            return value.isoformat()
        return str(value)

    def generate(self, tool: Tool) -> str:
        """Generate a filter example string.

        Args:
            tool: The tool to generate an example for

        Returns:
            Generated filter example string

        Raises:
            ValueError: If the filter function cannot be resolved
            TypeError: If the resolved object is not callable
        """
        if not callable(tool.filter_fn):
            msg = f"Resolved object {tool.import_path} is not callable"
            raise TypeError(msg)

        # Inspect the function to get its signature
        sig = inspect.signature(tool.filter_fn)

        # Get first parameter for the input value
        first_param = next(iter(sig.parameters.values()))
        example_input = self.get_example_value(first_param.annotation)
        formatted_input = self.format_value(example_input)

        # Generate filter arguments string for remaining parameters
        filter_kwargs = {
            name: self.get_example_value(param.annotation)
            for name, param in list(sig.parameters.items())[1:]
            if param.default is not param.empty
        }

        filter_args = ", ".join(f"{k}={v!r}" for k, v in filter_kwargs.items())

        # Create the template text
        if filter_args:
            template_text = f"{formatted_input}|{tool.name}({filter_args})"
        else:
            template_text = f"{formatted_input}|{tool.name}"

        return "{{ " + template_text + " }}"


if __name__ == "__main__":
    from toolreg.registry.tool import Tool

    # Create a sample tool
    tool = Tool(
        name="cos",
        typ="filter",
        import_path="math.cos",
    )

    # Generate an example using the strategy
    strategy = FilterExampleStrategy()
    example = strategy.generate(tool)
    print(f"Generated example: {example}")
    # Output: Generated example: {{ "Hello, World!"|prefix_filter(prefix='test_') }}
