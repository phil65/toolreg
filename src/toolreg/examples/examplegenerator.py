from __future__ import annotations

from toolreg.examples import examplestrategy
from toolreg.registry.tool import Tool


class ExampleGenerator:
    """Generator for tool examples using different strategies."""

    def __init__(self) -> None:
        """Initialize the example generator with default strategies."""
        self.strategies: dict[str, examplestrategy.ExampleStrategy] = {
            "filter": examplestrategy.FilterExampleStrategy(),
            # Add more strategies here as needed
            # "test": TestExampleStrategy(),
            # "function": FunctionExampleStrategy(),
        }

    def generate(self, tool: Tool) -> str:
        """Generate an example for the given tool.

        Args:
            tool: The tool to generate an example for

        Returns:
            Generated example string

        Raises:
            ValueError: If no strategy exists for the tool type
        """
        if strategy := self.strategies.get(tool.typ):
            return strategy.generate(tool)

        msg = f"No example generation strategy found for tool type: {tool.typ}"
        raise ValueError(msg)

    def add_strategy(
        self, tool_type: str, strategy: examplestrategy.ExampleStrategy
    ) -> None:
        """Add a new example generation strategy.

        Args:
            tool_type: The tool type this strategy handles
            strategy: The strategy implementation
        """
        self.strategies[tool_type] = strategy


if __name__ == "__main__":
    # Example usage
    tool = Tool(
        name="upper",
        typ="filter",
        import_path="str.upper",
    )

    # Add a custom strategy
    class CustomStrategy(examplestrategy.ExampleStrategy):
        def generate(self, tool: Tool) -> str:
            return f"Custom example for {tool.name}"

    generator = ExampleGenerator()
    # generator.add_strategy("custom", CustomStrategy())
    example = generator.generate(tool)
    print(example)
