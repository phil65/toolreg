"""Module for parsing Markdown code blocks with metadata."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field


# Type alias for regex match groups
type CodeBlockMatch = tuple[str, str, str | None]

# Regex patterns
CODE_BLOCK_PATTERN = re.compile(
    r"```(\w+)?(?:\s+([^`\n]*))??\n"  # Opening fence with language and metadata
    r"((?:.*\n)*?)"  # Content (non-greedy)
    r"```",  # Closing fence
    re.MULTILINE,
)

METADATA_PATTERN = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')


class CodeBlock(BaseModel):
    """Represents a parsed Markdown code block with metadata."""

    language: str = Field(default="text", description="Programming language")
    content: str = Field(..., description="Code block content")
    title: str | None = Field(default=None, description="Optional title")
    line_numbers: bool = Field(default=False, description="Show line numbers")
    highlight_lines: list[int] = Field(default_factory=list, description="Lines to highlight")


def parse_code_block(text: str) -> CodeBlock:
    """Parse a Markdown code block with metadata.

    Args:
        text: Raw markdown text containing a code block

    Returns:
        CodeBlock object containing parsed information
    """
    if not (match := CODE_BLOCK_PATTERN.search(text)):
        msg = "No valid code block found in text"
        raise ValueError(msg) from None

    language, metadata, content = match.groups()
    parsed = _parse_metadata(metadata or "")

    return CodeBlock(
        language=language or "text",
        content=content.rstrip(),
        title=parsed.get("title"),
        line_numbers="linenums" in parsed,
        highlight_lines=_parse_highlight_lines(parsed.get("hl_lines", "")),
    )


def parse_code_blocks(text: str) -> list[CodeBlock]:
    """Parse all Markdown code blocks with metadata from text.

    Args:
        text: Raw markdown text containing one or more code blocks

    Returns:
        List of CodeBlock objects containing parsed information
    """
    blocks: list[CodeBlock] = []

    for match in CODE_BLOCK_PATTERN.finditer(text):
        language, metadata, content = match.groups()
        parsed = _parse_metadata(metadata or "")

        blocks.append(
            CodeBlock(
                language=language or "text",
                content=content.rstrip(),
                title=parsed.get("title"),
                line_numbers="linenums" in parsed,
                highlight_lines=_parse_highlight_lines(parsed.get("hl_lines", "")),
            )
        )

    return blocks


def _parse_metadata(metadata: str) -> dict[str, str]:
    """Parse code block metadata into a dictionary."""
    result: dict[str, str] = {}

    for match in METADATA_PATTERN.finditer(metadata):
        key = match.group(1)
        # Take the quoted value if it exists, otherwise take the unquoted value
        value = match.group(2) if match.group(2) is not None else match.group(3)
        result[key] = value

    return result


def _parse_highlight_lines(hl_lines: str) -> list[int]:
    """Parse highlight lines specification into a list of line numbers."""
    if not hl_lines:
        return []

    result: list[int] = []
    for part in hl_lines.split():
        if match := re.match(r"(\d+)-(\d+)", part):
            start, end = map(int, match.groups())
            result.extend(range(start, end + 1))
        elif match := re.match(r"(\d+)", part):
            result.append(int(match.group(1)))

    return sorted(set(result))


if __name__ == "__main__":
    # Example markdown text
    markdown = """```python title="example.py" linenums="1" hl_lines="2 3"
def hello():
    print("Hello")
    return True
```"""

    code_block = parse_code_block(markdown)
    print(code_block.model_dump())
