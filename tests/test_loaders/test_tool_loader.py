"""Tests for the ToolLoader class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from toolreg.registry.loaders import ToolLoader
from toolreg.registry.loaders.base import LoaderError


if TYPE_CHECKING:
    from upath import UPath


def test_tool_loader_initialization() -> None:
    """Test ToolLoader creates all expected loaders."""
    loader = ToolLoader()
    expected_loaders = {"toml", "module", "plugin"}
    assert set(loader._active_loaders.keys()) == expected_loaders


def test_load_with_invalid_source(tool_loader: ToolLoader) -> None:
    """Test loading from an invalid source raises LoaderError."""
    with pytest.raises(LoaderError, match="No suitable loader found for"):
        tool_loader.load("nonexistent_source")


def test_load_many_continues_on_error(tool_loader: ToolLoader) -> None:
    """Test load_many continues processing after errors."""
    sources = ["invalid1", "invalid2"]
    tool_loader.load_many(sources)  # Should not raise, just log errors


def test_load_with_failing_loader(
    tool_loader: ToolLoader,
    example_toml_file: UPath,
) -> None:
    """Test handling of loader failures."""
    # Corrupt the TOML file
    example_toml_file.write_text("invalid toml content")

    with pytest.raises(LoaderError):
        tool_loader.load(str(example_toml_file))
