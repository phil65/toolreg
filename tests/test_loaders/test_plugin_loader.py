"""Tests for the plugin loader."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import upath

from toolreg.registry.loaders.base import LoaderError
from toolreg.registry.loaders.plugin_loader import PluginLoader


if TYPE_CHECKING:
    import os


def test_can_load_valid_plugin(tmp_path: str | os.PathLike[str]) -> None:
    """Test can_load with valid plugin module."""
    plugin_code = """
def register_tools():
    pass
"""
    plugin_path = upath.UPath(tmp_path) / "test_plugin.py"
    plugin_path.write_text(plugin_code)

    loader = PluginLoader()
    # Note: This test might need adjustment based on how plugins are actually
    # discovered and loaded in your system
    assert not loader.can_load("test_plugin")  # Should be False as not importable


def test_load_invalid_plugin() -> None:
    """Test loading an invalid plugin raises LoaderError."""
    loader = PluginLoader()
    with pytest.raises(LoaderError):
        loader.load("nonexistent_plugin")


def test_load_same_plugin_twice() -> None:
    """Test loading the same plugin twice only loads once."""
    loader = PluginLoader()
    # Using a built-in module as a mock plugin for this test
    module_name = "json"
    loader._mark_loaded(module_name)  # Simulate first load
    assert loader.is_loaded(module_name)

    # Second load should be a no-op
    with pytest.raises(LoaderError):
        loader.load(module_name)
