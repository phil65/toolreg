"""Module for extracting function documentation and examples."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

from upath import UPath
import yaml

from toolreg.dissect import detect_docstring_style


if TYPE_CHECKING:
    from collections.abc import Callable

type ExampleDict = dict[str, dict[str, str]]
type FuncInfo = dict[str, str | ExampleDict]


def get_qualified_name(func: Callable[..., Any]) -> str:
    """Get the fully qualified name of a function or method.

    Args:
        func: The function or method to inspect

    Returns:
        Fully qualified name as string

    Raises:
        ValueError: If function path cannot be determined
    """
    match func:
        case _ if inspect.ismethod(func):
            if hasattr(func, "__self__"):
                if inspect.isclass(func.__self__):  # classmethod
                    return f"{func.__self__.__module__}.{func.__qualname__}"
                # instance method
                return f"{func.__self__.__class__.__module__}.{func.__qualname__}"
            # static method
            return f"{func.__module__}.{func.__qualname__}"
        case _ if inspect.isfunction(func):
            return f"{func.__module__}.{func.__qualname__}"
        case _ if hasattr(func, "__module__") and hasattr(func, "__qualname__"):
            return f"{func.__module__}.{func.__qualname__}"
        case _:
            msg = f"Could not determine import path for {func}"
            raise ValueError(msg)


def inspect_function(func: Callable[..., Any]) -> FuncInfo:
    """Extract function documentation and examples from docstring.

    Args:
        func: The function to inspect

    Returns:
        Dictionary containing function info, description and examples

    Examples:
        >>> def example_func(x: int) -> str:
        ...     '''Format a number.
        ...
        ...     Examples:
        ...         >>> example_func(42)
        ...         "Number: 42"
        ...     '''
        ...     return f"Number: {x}"
        >>> result = inspect_function(example_func)
        >>> result['description']
        'Format a number.'
    """
    if not callable(func):
        msg = "Argument must be a callable"
        raise TypeError(msg)

    # Get function's qualified name
    try:
        full_path = get_qualified_name(func)
    except ValueError as e:
        msg = "Failed to determine function path"
        raise ValueError(msg) from e

    # Get docstring safely
    docstring = inspect.getdoc(func) or ""

    # Detect style and parse docstring
    style = detect_docstring_style.detect_docstring_style(docstring)
    doc = detect_docstring_style.parse_docstring(docstring, style=style.value)

    # Initialize result dictionary
    result: FuncInfo = {
        "fn": full_path,
        "description": "",
    }

    # Extract description from parsed sections
    for section in doc:
        if section.kind == "text":
            result["description"] = section.value.strip()
            break

    # Extract examples from parsed sections
    examples: ExampleDict = {}
    for section in doc:
        if section.kind == "examples":
            for i, example in enumerate(section.value):
                example_name = f"example_{i + 1}" if len(section.value) > 1 else "basic"
                if example_text := str(example).strip():
                    examples[example_name] = {"template": example_text}

    if examples:
        result["examples"] = examples

    return result


def generate_function_docs(
    functions: list[Callable[..., Any]], output_path: str | UPath | None = None
) -> dict[str, FuncInfo]:
    """Generate documentation dictionary for multiple functions.

    Args:
        functions: List of functions to document
        output_path: Optional path to save the output

    Returns:
        Dictionary containing all function documentation

    Examples:
        >>> def func1(x: int) -> str:
        ...     '''First function'''
        ...     return str(x)
        >>> def func2(y: str) -> str:
        ...     '''Second function'''
        ...     return y.upper()
        >>> docs = generate_function_docs([func1, func2])
        >>> len(docs)
        2
    """
    result = {
        func.__name__: inspect_function(func)
        for func in functions
        if not func.__name__.startswith("_")
    }

    if output_path:
        path = UPath(output_path)
        match path.suffix.lower():
            case ".yaml" | ".yml":
                path.write_text(yaml.dump(result, sort_keys=False))
            case ".json":
                import json

                path.write_text(json.dumps(result, indent=2))
            case _:
                msg = "Unsupported output format. Use .yaml, .yml, or .json"
                raise ValueError(msg)

    return result


if __name__ == "__main__":
    import inspect

    def test(a: int = 0, b: str = "abc"):
        """Test funcion.

        Some text.

        Args:
            a: An integer
            b: A string

        Examples:
            ``` py
            >>> test(42, "xyz")
            ````

            ``` py
            >>> test(0, "abc")
            ```
        """

    result = inspect_function(test)
    print(result)
