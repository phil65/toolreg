from __future__ import annotations

from pydantic import BaseModel, Field


class Example(BaseModel):
    """Example model for jinja items."""

    # content: str = Field(description="Template content to render")
    template: str = Field(description="The input string or expression for the example")
    title: str = Field(default="", description="Title of the example")
    description: str | None = Field(default=None, description="Example description")
    markdown: bool = Field(default=False, description="Whether content is markdown")


ExampleDict = dict[str, Example]
