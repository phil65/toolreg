"""Markdown-based tool definition parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import mistune  # lightweight markdown parser
from pydantic import BaseModel, Field


@dataclass
class CodeBlock:
    """Code block extracted from markdown."""

    content: str
    language: str | None = None

    def __str__(self) -> str:
        return self.content


class Example(BaseModel):
    """Example usage of a tool."""

    title: str
    description: str | None = None
    content: str
    language: Literal["python", "jinja"] = "python"


class ToolDefinition(BaseModel):
    """Complete tool definition from markdown."""

    name: str
    description: str = ""
    config: dict[str, Any] = Field(default_factory=dict)  # will contain yaml config
    implementation: CodeBlock
    examples: list[Example] = Field(default_factory=list)


class MarkdownToolParser:
    """Parser for markdown-based tool definitions."""

    def __init__(self):
        self.md = mistune.create_markdown(renderer=mistune.AstRenderer())

    def parse(self, content: str) -> ToolDefinition:
        """Parse markdown content into a tool definition."""
        ast = self.md(content)

        # Initialize collection variables
        name = ""
        description = []
        config_block = None
        implementation_block = None
        current_example: dict[str, Any] | None = None
        examples = []

        for node in ast:
            match node:
                case {"type": "heading", "level": 1, "children": [{"text": title}]}:
                    name = title.strip()

                case {"type": "paragraph"} if not name:
                    # Description before any other sections
                    description.extend(self._extract_text(node))

                case {
                    "type": "heading",
                    "level": 2,
                    "children": [{"text": "Configuration"}],
                }:
                    config_block = self._find_next_code_block(ast, node, "yaml")

                case {
                    "type": "heading",
                    "level": 2,
                    "children": [{"text": "Implementation"}],
                }:
                    implementation_block = self._find_next_code_block(ast, node, "python")

                case {"type": "heading", "level": 3, "children": [{"text": title}]} if (
                    implementation_block
                ):
                    # Example section (only process after implementation)
                    if current_example:
                        examples.append(Example(**current_example))
                    current_example = {"title": title}

                case {"type": "paragraph"} if (
                    current_example and "content" not in current_example
                ):
                    # Example description
                    current_example["description"] = " ".join(self._extract_text(node))

                case {"type": "code"} if current_example:
                    # Example code
                    current_example.update({
                        "content": node["text"],
                        "language": node.get("lang", "python"),
                    })

        # Add final example if any
        if current_example and "content" in current_example:
            examples.append(Example(**current_example))

        if not name:
            msg = "No tool name found (level 1 heading)"
            raise ValueError(msg)

        if not implementation_block:
            msg = "No implementation found"
            raise ValueError(msg)

        # Parse YAML config if present
        config = {}
        if config_block:
            import yaml

            config = yaml.safe_load(config_block.content)

        return ToolDefinition(
            name=name,
            description=" ".join(description),
            config=config,
            implementation=implementation_block,
            examples=examples,
        )

    def _extract_text(self, node: dict) -> list[str]:
        """Extract text from a node and its children."""
        texts = []
        if text := node.get("text"):
            texts.append(text)
        for child in node.get("children", []):
            texts.extend(self._extract_text(child))
        return texts

    def _find_next_code_block(
        self, ast: list[dict], after_node: dict, language: str | None = None
    ) -> CodeBlock | None:
        """Find the next code block after a specific node."""
        found_node = False
        for node in ast:
            if node == after_node:
                found_node = True
                continue

            if not found_node:
                continue

            if node["type"] == "code" and (
                language is None or node.get("lang") == language
            ):
                return CodeBlock(content=node["text"], language=node.get("lang"))
        return None
