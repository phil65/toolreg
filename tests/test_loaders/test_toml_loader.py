"""Tests for the TOML loader."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from toolreg.registry.loaders.base import LoaderError
from toolreg.registry.loaders.toml_loader import TomlLoader


if TYPE_CHECKING:
    from upath import UPath


def test_can_load_valid_toml(example_toml_file: UPath) -> None:
    """Test can_load with valid TOML file."""
    loader = TomlLoader()
    assert loader.can_load(str(example_toml_file))


def test_can_load_invalid_file(tmp_path: UPath) -> None:
    """Test can_load with non-TOML file."""
    invalid_file = tmp_path / "not_a_toml_file.txt"
    invalid_file.touch()
    loader = TomlLoader()
    assert not loader.can_load(str(invalid_file))


def test_load_invalid_toml(tmp_path: UPath) -> None:
    """Test loading invalid TOML content."""
    invalid_toml = tmp_path / "invalid.toml"
    invalid_toml.write_text("invalid = toml [ content")

    loader = TomlLoader()
    with pytest.raises(LoaderError):
        loader.load(str(invalid_toml))


def test_load_same_file_twice(example_toml_file: UPath) -> None:
    """Test loading the same file twice only processes it once."""
    loader = TomlLoader()

    # First load
    loader.load(str(example_toml_file))
    initial_count = len(loader._registry._items)

    # Second load
    loader.load(str(example_toml_file))
    final_count = len(loader._registry._items)

    assert final_count == initial_count, "Tools should not be registered twice"
