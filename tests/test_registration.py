"""Tests for tool registration functionality."""

from __future__ import annotations

import pytest

from toolreg import register_tool
from toolreg.registry import example, registry


def test_register_tool_decorator():
    """Test registration via decorator."""
    reg = registry.ToolRegistry()
    initial_count = len(reg.get_all(typ="filter"))

    @register_tool(
        typ="filter",
        group="text",
        examples=[
            example.Example(
                template="{{ 'test' | upper }}",
                title="Test Example",
            )
        ],
    )
    def upper(value: str) -> str:
        """Convert string to uppercase."""
        return value.upper()

    # Verify registration
    tools = reg.get_all(typ="filter")
    assert len(tools) == initial_count + 1

    # Find our registered function
    registered_funcs = {name: func for name, (func, _) in tools.items()}
    assert "upper" in registered_funcs

    # Test the function actually works
    test_value = "hello"
    assert registered_funcs["upper"](test_value) == test_value.upper()


def test_register_tool_with_metadata():
    """Test registration with full metadata."""
    reg = registry.ToolRegistry()
    initial_count = len(reg.get_all(typ="filter"))

    @register_tool(
        typ="filter",
        name="custom_upper",
        group="text",
        description="Custom uppercase filter",
        examples=[
            example.Example(
                template="{{ 'test' | custom_upper }}",
                title="Basic Example",
            )
        ],
        required_packages=["toolreg"],
        aliases=["c_upper"],
        icon="mdi:format-letter-case-upper",
    )
    def upper(value: str) -> str:
        """Convert string to uppercase."""
        return value.upper()

    # Verify registration
    tools = reg.get_all(typ="filter")
    assert len(tools) == initial_count + 2  # +2 because of alias

    # Check both main name and alias
    for name in ["custom_upper", "c_upper"]:
        assert name in tools
        func, metadata = tools[name]
        # Test function works
        assert func("test") == "TEST"
        # Check metadata
        assert metadata.description == "Custom uppercase filter"
        assert metadata.group == "text"
        assert metadata.icon == "mdi:format-letter-case-upper"


def test_register_tool_validation():
    """Test validation during registration."""
    with pytest.raises(ValueError, match="Failed to create*"):

        @register_tool(typ="invalid_type")  # type: ignore
        def test_func():
            pass


if __name__ == "__main__":
    pytest.main([__file__])
