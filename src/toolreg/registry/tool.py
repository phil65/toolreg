from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

from toolreg.utils import resolve


class Example(BaseModel):
    """Represents an example for a Jinja item."""

    template: str = Field(description="The input string or expression for the example")
    markdown: bool = Field(True, description="Whether the example needs markdown fencing")
    description: str = Field("", description="Description of the example")


class Tool(BaseModel):
    """An item representing a filter, test, or function in Jinja."""

    identifier: str = Field(description="Unique identifier for the Jinja item")
    typ: Literal["filter", "test", "function"] = Field(
        description="Type of the Jinja item: filter, test, or function"
    )
    fn: str = Field(description="The function name or reference for the Jinja item")
    group: str = Field(description="The group or category this item belongs to")
    examples: dict[str, Example] = Field(
        default_factory=dict,
        description="Dictionary of named examples demonstrating the item's usage",
    )
    description: str | None = Field(
        default=None,
        description="Optional description of the Jinja item's purpose and behavior",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description="List of alternative names or aliases for the item",
    )
    required_packages: list[str] = Field(
        default_factory=list,
        description="List of package names required for this item to function",
    )

    @property
    def filter_fn(self) -> Callable[..., Any]:
        """Return the callable to use as filter / test / function."""
        try:
            obj = resolve.resolve(self.fn)
        except AttributeError:
            msg = f"Could not import jinja item {self.identifier!r} from {self.fn!r}"
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

    class Config:
        frozen = True
