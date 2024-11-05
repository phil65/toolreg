from typing import Literal

from pydantic import BaseModel, Field


class Example(BaseModel):
    """Represents an example for a Jinja item."""

    input: str = Field(description="The input string or expression for the example")
    output: str = Field(description="The expected output of the example")


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

    class Config:
        frozen = True
