"""Custom types for string validation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from pydantic import GetCoreSchemaHandler
from pydantic_core.core_schema import str_schema


if TYPE_CHECKING:
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import CoreSchema


class SlugField:
    """Field type for slug validation."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return str_schema(
            pattern=r"^[a-zA-Z0-9_]+$",
            to_lower=True,
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: CoreSchema,
        _handler: GetCoreSchemaHandler,
    ) -> JsonSchemaValue:
        return {
            "type": "string",
            "pattern": "^[a-zA-Z0-9_]+$",
            "description": "Slug string (alphanumeric and underscore only)",
        }


Slug = Annotated[str, SlugField()]


if __name__ == "__main__":
    from pydantic import BaseModel, Field

    class BlogPost(BaseModel):
        slug: Slug = Field(description="URL-friendly identifier")

    test = BlogPost(slug="Ü")
