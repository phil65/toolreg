from __future__ import annotations

from typing import Literal

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
