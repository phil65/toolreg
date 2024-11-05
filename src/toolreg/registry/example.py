from __future__ import annotations

from pydantic import BaseModel, Field


class Example(BaseModel):
    """Example model for tool documentation."""

    template: str = Field(description="Template code for the example")
    title: str = Field(description="Example title")
    description: str = Field(description="Example description")
    markdown: bool = Field(default=False, description="Whether content is markdown")


ExampleDict = dict[str, Example]
