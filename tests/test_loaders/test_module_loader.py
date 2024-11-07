"""Tests for the module loader."""

from __future__ import annotations

import pytest

from toolreg.registry.loaders.base import LoaderError
from toolreg.registry.loaders.module_loader import ModuleLoader


def test_can_load_existing_module() -> None:
    """Test can_load with existing Python module."""
    loader = ModuleLoader()
    assert loader.can_load("json")  # built-in module


def test_can_load_nonexistent_module() -> None:
    """Test can_load with non-existent module."""
    loader = ModuleLoader()
    assert not loader.can_load("nonexistent_module_xyz")


def test_load_invalid_module() -> None:
    """Test loading an invalid module raises LoaderError."""
    loader = ModuleLoader()
    with pytest.raises(LoaderError):
        loader.load("nonexistent_module_xyz")


def test_load_same_module_twice() -> None:
    """Test loading the same module twice only loads once."""
    loader = ModuleLoader()
    loader.load("json")  # built-in module
    assert loader.is_loaded("json")

    # Second load should be a no-op
    loader.load("json")
