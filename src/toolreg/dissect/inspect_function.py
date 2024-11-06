"""Module for extracting function documentation and examples."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, TypedDict

from upath import UPath
import yaml

from toolreg.registry import example


if TYPE_CHECKING:
    from collections.abc import Callable


class FuncInfo(TypedDict):
    fn: str
    description: str
    examples: example.ExampleList


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

    # Unwrap decorators to get to the original function
    original_fn = inspect.unwrap(func)

    # Get function's qualified name
    try:
        full_path = get_qualified_name(original_fn)
    except ValueError as e:
        msg = "Failed to determine function path"
        raise ValueError(msg) from e

    # Get docstring safely
    docstring = inspect.getdoc(original_fn) or ""
    from toolreg.dissect import docstringstyler

    # Detect style and parse docstring
    style = docstringstyler.detect_docstring_style(docstring)
    doc = docstringstyler.parse_docstring(docstring, style=style.value)

    # Initialize result dictionary
    result: FuncInfo = {"fn": full_path, "description": "", "examples": []}

    # Extract description and examples
    for section in doc:
        match section.kind:
            case "text":
                result["description"] = section.value.strip()
            case "examples":
                examples = [
                    example.Example(template=str(ex).strip())
                    for ex in section.value
                    if str(ex).strip()
                ]
                result["examples"].extend(examples)
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


def get_qualified_name(func: Any) -> str:
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
