from collections.abc import Callable
from typing import Any, Self

from pydantic import BaseModel, Field

from toolreg.dissect import inspect_function
from toolreg.registry import example
from toolreg.registry.registry import FilterFunc, ItemType
from toolreg.utils import resolve, slugfield


class Example(BaseModel):
    """Example model for jinja items."""

    # content: str = Field(description="Template content to render")
    template: str = Field(description="The input string or expression for the example")
    title: str = Field(default="", description="Title of the example")
    description: str | None = Field(default=None, description="Example description")
    markdown: bool = Field(default=False, description="Whether content is markdown")


class ToolMetadata(BaseModel):
    """Metadata for a jinja item."""

    name: slugfield.Slug
    """ame of the jinja item"""
    typ: ItemType
    """type of the item (filter, test, or function)"""
    import_path: str
    """mport path in the format "package.module.function"""
    description: str | None = None
    """ptional description of what the item does"""
    group: str = "general"
    """roup/category for organizing items"""
    # examples: list[Example] = Field(default_factory=list)
    examples: dict[str, Example] = Field(default_factory=dict)
    # or dict[str, Example] ?
    """ist of usage examples"""
    required_packages: list[str] = Field(default_factory=list)
    """ython packages required for this item"""
    aliases: list[str] = Field(default_factory=list)
    """lternative names that can be used to access this item"""
    icon: str | None = None
    """ptional icon identifier"""

    @classmethod
    def from_function(
        cls,
        func: FilterFunc,
        *,
        typ: ItemType,
        name: str | None = None,
        group: str | None = None,
        examples: example.ExampleDict | None = None,
        required_packages: list[str] | None = None,
        aliases: list[str] | None = None,
        icon: str | None = None,
        description: str | None = None,
    ) -> Self:
        """Create metadata from a function's attributes and docstring.

        Args:
            func: The function to create metadata for
            typ: Type of item (filter, test, function)
            name: Optional override for the function name
            group: Group/category for organization
            examples: Dictionary of named examples
            required_packages: List of required package names
            aliases: List of alternative names
            icon: Icon identifier (e.g. mdi:home)
            description: Optional override for function description

        Returns:
            New ToolMetadata instance configured with the provided data

        Example:
            ```python
            def my_filter(value: str) -> str:
                '''Convert string to uppercase.
                    >>> my_filter('hello')
                    'HELLO'
                '''
                return value.upper()

            metadata = ToolMetadata.from_function(
                my_filter,
                typ="filter",
                group="text",
                icon="mdi:format-letter-case-upper"
            )
            ```
        """
        # Get base metadata from inspect_function
        extracted = inspect_function.inspect_function(func)

        # Convert examples to Example model instances
        extracted_examples = {
            name: Example.model_validate(ex)
            for name, ex in extracted.get("examples", {}).items()
        }

        # If examples provided in kwargs, use those instead
        final_examples = extracted_examples
        if examples is not None:
            final_examples = {
                name: Example.model_validate(example)
                for name, example in examples.items()
            }

        # Build metadata dict with explicit precedence
        metadata = {
            "name": name if name is not None else func.__name__,
            "typ": typ,
            "import_path": extracted["fn"],
            "description": (
                description if description is not None else extracted.get("description")
            ),
            "examples": final_examples,
            "group": group if group is not None else "general",
            "required_packages": required_packages
            if required_packages is not None
            else [],
            "aliases": aliases if aliases is not None else [],
            "icon": icon,
        }

        return cls.model_validate(metadata)

    @property
    def filter_fn(self) -> Callable[..., Any]:
        """Return the callable to use as filter / test / function."""
        try:
            obj = resolve.resolve(self.import_path)
        except AttributeError:
            msg = f"Could not import jinja item {self.name!r} from {self.import_path!r}"
            raise ImportError(msg) from AttributeError
        if not callable(obj):
            msg = "Filter needs correct, importable Path for callable"
            raise TypeError(msg)
        return obj

    def apply(self, *args: Any, **kwargs: Any) -> Any:
        """Apply the filter function using given arguments and keywords.

        Args:
            args: The arguments for the call
            kwargs: They keyword arguments for the call
        """
        return self.filter_fn(*args, **kwargs)
