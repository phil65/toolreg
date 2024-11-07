"""Integration tests for loaders and registration."""

from __future__ import annotations

from toolreg import register_tool
from toolreg.registry.loaders import ToolLoader


def test_loader_with_decorated_functions(example_toml_file):
    """Test loader works alongside decorator-based registration."""

    @register_tool(typ="filter", group="text")
    def test_filter(value: str) -> str:
        """Test filter."""
        return value.upper()

    loader = ToolLoader()
    # Load from TOML file
    loader.load(str(example_toml_file))

    # Both decorated function and TOML-loaded tools should be available
    reg = loader._active_loaders["toml"]._registry
    filters = reg.get_all(typ="filter")
    assert "test_filter" in filters
    assert "upper_filter" in filters
    assert "lower_filter" in filters
