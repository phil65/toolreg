from collections.abc import Iterable, Iterator, Iterator as ABCIterator
from inspect import signature
from types import NoneType
from typing import Union, get_args, get_origin, get_type_hints


def inspect_function(func) -> str:
    """Inspects a function and categorizes it based on its signature and return type.

    1. "filter" if:
    - The function has type hints
    - The first parameter involves a string type (either directly or in a Union)
    - The return type involves a string type

    2. "iterator" if:
    - The return type is a subclass of Iterator, ABCIterator, or Iterable
    - The return type has a custom `__iter__` method

    3. "test" if:
    - The return type is explicitly boolean

    4. "function" if:
    - The function has type hints
    - The return type is specified
    - It doesn't match any of the above categories

    5. "unknown" if:
    - The function is not callable
    - No return type is specified
    - The return type is None
    - There are missing type hints
    - There's an error accessing the function's signature

    Args:
        func: The function to inspect

    Returns:
        str: One of "filter", "iterator", "test", "function", or "unknown"
    """
    if not callable(func):
        msg = "Input must be a callable"
        raise TypeError(msg)

    try:
        # Get type hints and signature
        type_hints = get_type_hints(func)

        # Check if return type is specified
        if "return" not in type_hints:
            return "unknown"

        return_type = type_hints["return"]

        # Check for None return type
        if return_type is None or return_type is NoneType:
            return "unknown"

        sig = signature(func)
        params = list(sig.parameters.values())

        # Handle empty parameter list
        if not params:
            return _categorize_by_return_type(return_type)

        # Get first parameter type
        first_param_name = params[0].name
        first_param_type = type_hints.get(first_param_name, type(None))

        # Check if first parameter involves str and return type is str
        if _involves_str(first_param_type) and _involves_str(return_type):
            return "filter"

        return _categorize_by_return_type(return_type)

    except (ValueError, TypeError, AttributeError):
        return "unknown"


def _involves_str(type_hint) -> bool:
    """Check if a type hint involves str (either directly or in a Union)."""
    if type_hint is str:
        return True

    origin = get_origin(type_hint)
    if origin is Union or origin is not None:
        args = get_args(type_hint)
        return str in args or any(_involves_str(arg) for arg in args)

    return False


def _categorize_by_return_type(return_type) -> str:
    """Categorize function based on return type."""
    if return_type is bool:
        return "test"

    # Get the origin type for generic types
    origin = get_origin(return_type)
    if origin is not None and issubclass(origin, (Iterator, ABCIterator, Iterable)):
        return "iterator"

    # Check for direct iterator/iterable types
    if isinstance(return_type, type):
        if issubclass(return_type, (Iterator, ABCIterator, Iterable)):
            return "iterator"
        if (
            hasattr(return_type, "__iter__") and return_type.__iter__ is not object.__iter__  # type: ignore
        ):
            return "iterator"

    return "function"


# Test cases
def test_inspect_function():
    # Filter function (str -> str)
    def str_to_str(text: str) -> str:
        return text.upper()

    # Filter function with union type using |
    def process_input(data: str | int) -> str:
        return str(data)

    # Iterator function
    def get_numbers() -> Iterator[int]:
        yield from range(10)

    # Test function
    def is_valid(x: int) -> bool:
        return x > 0

    # Regular function
    def add(x: int, y: int) -> int:
        return x + y

    # Function without return type
    def print_something(x: str):
        print(x)

    # Function returning None
    def do_something(x: int) -> None:
        print(x)

    # Function with only parameter types
    def process(data: str | int):
        return str(data)

    # Function without any type hints
    def no_hints(x):
        return x

    assert inspect_function(str_to_str) == "filter"
    assert inspect_function(process_input) == "filter"
    assert inspect_function(get_numbers) == "iterator"
    assert inspect_function(is_valid) == "test"
    assert inspect_function(add) == "function"
    assert inspect_function(print_something) == "unknown"
    assert inspect_function(do_something) == "unknown"
    assert inspect_function(process) == "unknown"
    assert inspect_function(no_hints) == "unknown"

    print("All tests passed!")


if __name__ == "__main__":
    test_inspect_function()
