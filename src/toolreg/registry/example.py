from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Example(BaseModel):
    """Example model for jinja items."""

    # content: str = Field(description="Template content to render")
    template: str = Field(description="The input string or expression for the example")
    title: str = Field(default="", description="Title of the example")
    description: str | None = Field(default=None, description="Example description")
    markdown: bool = Field(default=False, description="Whether content is markdown")
    language: Literal["jinja", "python"] = Field(
        default="jinja",
        description="The language of the example (jinja or python)",
    )


ExampleList = list[Example]


def get_example_value(type_hint: Any) -> Any:
    """Generate a realistic example value based on a type hint.

    Args:
        type_hint: The type hint to generate an example for

    Returns:
        An appropriate example value for the given type
    """
    import datetime
    import decimal
    import enum
    import inspect
    import ipaddress
    import pathlib
    import re
    import typing
    import uuid

    if type_hint in (inspect.Parameter.empty, Any):
        return "example_text"

    # Handle Optional/Union types
    origin = typing.get_origin(type_hint)
    if origin is not None:
        args = typing.get_args(type_hint)
        if origin == typing.Union:
            # For Optional/Union types, use the first non-None type
            for arg in args:
                if arg != type(None):  # noqa: E721
                    return get_example_value(arg)
        if origin in (list, list):
            return [get_example_value(args[0])] if args else [1, 2, 3]
        if origin in (dict, dict):
            key_type = args[0] if args else str
            value_type = args[1] if len(args) > 1 else Any
            return {get_example_value(key_type): get_example_value(value_type)}

        type_mapping = {
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
            type: type("Example", (), {}),
            datetime.date: datetime.date(2024, 1, 1),
            datetime.time: datetime.time(12, 0),
            datetime.datetime: datetime.datetime(2024, 1, 1, 12, 0),
            datetime.timedelta: datetime.timedelta(days=1),
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

        if value := type_mapping.get(type_hint):
            return value
    # For unknown types, return a string representation
    return f"example_{type_hint.__name__.lower()}"


# def generate_filter_example(tool: Tool) -> str:
#     """Generate a string showing how to use the tool as a Jinja filter.

#     Args:
#         tool: Tool instance containing the filter information

#     Returns:
#         A string containing the filter usage example

#     Examples:
#         >>> tool = Tool(
#         ...     name="upper",
#         ...     typ="filter",
#         ...     import_path="str.upper"
#         ... )
#         >>> generate_filter_example(tool)
#         '{{ "hello"|upper }}'
#     """
#     try:
#         fn = resolve.resolve(tool.import_path)
#     except AttributeError as e:
#         msg = f"Could not resolve filter function from {tool.import_path}"
#         raise ValueError(msg) from e

#     if not callable(fn):
#         msg = f"Resolved object {tool.import_path} is not callable"
#         raise TypeError(msg)

#     # Inspect the function to get its signature
#     sig = inspect.signature(fn)

#     # Get first parameter for the input value
#     first_param = next(iter(sig.parameters.values()))
#     example_input = get_example_value(first_param.annotation)

#     # Format the example input based on its type
#     if isinstance(example_input, str):
#         formatted_input = f'"{example_input}"'
#     elif isinstance(example_input, (dt.datetime, dt.date)):
#         formatted_input = example_input.isoformat()
#     elif isinstance(example_input, bytes):
#         formatted_input = str(example_input)
#     else:
#         formatted_input = str(example_input)

#     # Generate filter arguments string for remaining parameters
#     filter_kwargs = {
#         name: get_example_value(param.annotation)
#         for name, param in list(sig.parameters.items())[1:]
#         if param.default is not param.empty
#     }

#     filter_args = ", ".join(f"{k}={v!r}" for k, v in filter_kwargs.items())

#     # Create the template text
#     if filter_args:
#         template_text = f"{formatted_input}|{tool.name}({filter_args})"
#     else:
#         template_text = f"{formatted_input}|{tool.name}"

#     return "{{ " + template_text + " }}"
