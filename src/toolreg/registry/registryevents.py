from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import TYPE_CHECKING, Any, Protocol, TypedDict

from pydantic import BaseModel, ConfigDict, Field
import upath


if TYPE_CHECKING:
    from collections.abc import Callable
    import os


logger = logging.getLogger(__name__)


# Custom types
type FunctionArgs = tuple[Any, ...]
type FunctionKwargs = dict[str, Any]


class ErrorContext(TypedDict):
    """Type definition for error context information."""

    function: str
    args: FunctionArgs
    kwargs: FunctionKwargs


class ExecutionContext(BaseModel):
    """Immutable execution context containing function execution details.

    Attributes:
        function_name: Name of the executed function
        args: Positional arguments passed to the function
        kwargs: Keyword arguments passed to the function
        start_time: Function execution start timestamp
        result: Optional function execution result
        error: Optional exception if execution failed

    Example:
        ```python
        ctx = ExecutionContext(
            function_name="my_func",
            args=(1, 2),
            kwargs={"verbose": True},
            start_time=datetime.now()
        )
        ```
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    function_name: str = Field(..., description="Name of the executed function")
    args: FunctionArgs = Field(default_factory=tuple, description="Positional arguments")
    kwargs: FunctionKwargs = Field(default_factory=dict, description="Keyword arguments")
    start_time: datetime = Field(..., description="Execution start timestamp")
    result: Any | None = Field(None, description="Function execution result")
    error: Exception | None = Field(None, description="Exception if execution failed")


class RegistryEvents(Protocol):
    """Protocol defining registry event handlers interface.

    This protocol defines the contract for implementing registry event handlers.
    Any class implementing this protocol must provide methods for handling:
    - Function registration
    - Pre-execution events
    - Post-execution events
    - Error events

    Note:
        This is a Protocol class, meaning it defines an interface that classes
        can implement without explicit inheritance.

    Example:
        ```python
        class MyEvents(RegistryEvents):
            def on_register(self, func, metadata):
                print(f"Registered {func.__name__}")
        ```
    """

    def on_register(self, func: Callable[..., Any], metadata: dict[str, Any]) -> None:
        """Handle function registration events.

        Args:
            func: Function being registered
            metadata: Additional metadata for the function

        Note:
            This method is called when a function is first registered with the system.
        """

    def pre_execute(self, context: ExecutionContext) -> None:
        """Handle pre-execution events.

        Args:
            context: Execution context containing function details

        Warning:
            This method must be called before function execution to ensure proper
            event handling and metrics collection.
        """

    def post_execute(
        self, context: ExecutionContext, duration: float, end_time: datetime
    ) -> None:
        """Handle post-execution events.

        Args:
            context: Execution context with function results
            duration: Execution duration in seconds
            end_time: Execution end timestamp

        Note:
            This method is called regardless of whether the function execution
            succeeded or failed.
        """

    def on_error(self, error: Exception, context: ErrorContext) -> None:
        """Handle error events.

        Args:
            error: Exception that occurred
            context: Error context information

        Info:
            The context dictionary contains function name, arguments, and any
            additional information relevant to the error.
        """


class BaseRegistryEvents(ABC):
    """Abstract base class for registry events with required implementations.

    This class serves as a foundation for implementing registry event handlers.
    All concrete event handlers should inherit from this class.

    Example:
        ```python
        class MyEventHandler(BaseRegistryEvents):
            def on_register(self, func, metadata):
                # Implementation
                pass

            def pre_execute(self, context):
                # Implementation
                pass

            def post_execute(self, context, duration, end_time):
                # Implementation
                pass

            def on_error(self, error, context):
                # Implementation
                pass
        ```

    Warning:
        All abstract methods must be implemented by concrete subclasses.
    """

    @abstractmethod
    def on_register(self, func: Callable[..., Any], metadata: dict[str, Any]) -> None:
        """Handle function registration.

        Args:
            func: Function being registered
            metadata: Additional metadata for the function

        Raises:
            NotImplementedError: If not implemented by concrete class
        """

    @abstractmethod
    def pre_execute(self, context: ExecutionContext) -> None:
        """Handle pre-execution events."""

    @abstractmethod
    def post_execute(
        self, context: ExecutionContext, duration: float, end_time: datetime
    ) -> None:
        """Handle post-execution events."""

    @abstractmethod
    def on_error(self, error: Exception, context: dict[str, Any]) -> None:
        """Handle error events."""


class MetricsRegistryEvents(BaseRegistryEvents):
    """Collect and track metrics about function execution."""

    def __init__(self) -> None:
        self.registration_count: dict[str, int] = {}
        self.execution_count: dict[str, int] = {}
        self.error_count: dict[str, int] = {}
        self.execution_times: dict[str, list[float]] = {}

    def on_register(self, func: Callable[..., Any], metadata: dict[str, Any]) -> None:
        name = func.__name__
        self.registration_count[name] = self.registration_count.get(name, 0) + 1
        logger.info("Registered function: %s with metadata: %s", name, metadata)

    def pre_execute(self, context: ExecutionContext) -> None:
        name = context.function_name
        self.execution_count[name] = self.execution_count.get(name, 0) + 1
        logger.debug("Starting execution of %s", name)

    def post_execute(
        self, context: ExecutionContext, duration: float, end_time: datetime
    ) -> None:
        name = context.function_name
        times: list[float] = self.execution_times.setdefault(name, [])
        times.append(duration)

        status = "error" if context.error else "success"
        logger.debug("Completed %s with %s in %.2fs", name, status, duration)

    def on_error(self, error: Exception, context: dict[str, Any]) -> None:
        name = context["function"]
        self.error_count[name] = self.error_count.get(name, 0) + 1
        logger.error("Error in %s: %s", name, error)

    def get_metrics(self, function_name: str) -> dict[str, Any]:
        """Get collected metrics for a specific function."""
        times = self.execution_times.get(function_name, [])
        avg_duration = sum(times) / len(times) if times else 0

        return {
            "registrations": self.registration_count.get(function_name, 0),
            "executions": self.execution_count.get(function_name, 0),
            "errors": self.error_count.get(function_name, 0),
            "avg_duration": avg_duration,
            "min_duration": min(times) if times else 0,
            "max_duration": max(times) if times else 0,
        }


class LoggingRegistryEvents(BaseRegistryEvents):
    """Log registry events to a file."""

    def __init__(self, log_file: str | os.PathLike[str]) -> None:
        self.log_file: upath.UPath = upath.UPath(log_file)

    def _log(self, message: str) -> None:
        """Write a timestamped message to the log file."""
        with self.log_file.open("a") as f:
            f.write(f"{datetime.now()}: {message}\n")

    def on_register(self, func: Callable[..., Any], metadata: dict[str, Any]) -> None:
        self._log(f"Registered {func.__name__} with metadata: {metadata}")

    def pre_execute(self, context: ExecutionContext) -> None:
        self._log(
            f"Executing {context.function_name} "
            f"with args={context.args}, kwargs={context.kwargs}"
        )

    def post_execute(
        self, context: ExecutionContext, duration: float, end_time: datetime
    ) -> None:
        status = "error" if context.error else "success"
        self._log(
            f"Completed {context.function_name} with {status} "
            f"in {duration:.2f}s: result={context.result}"
        )

    def on_error(self, error: Exception, context: dict[str, Any]) -> None:
        self._log(f"Error in {context['function']}: {error}")


class CompositeEvents(BaseRegistryEvents):
    """Combine multiple event handlers into one."""

    def __init__(self, handlers: list[BaseRegistryEvents]) -> None:
        self.handlers: list[BaseRegistryEvents] = handlers

    def on_register(self, func: Callable[..., Any], metadata: dict[str, Any]) -> None:
        for handler in self.handlers:
            handler.on_register(func, metadata)

    def pre_execute(self, context: ExecutionContext) -> None:
        for handler in self.handlers:
            handler.pre_execute(context)

    def post_execute(
        self, context: ExecutionContext, duration: float, end_time: datetime
    ) -> None:
        for handler in self.handlers:
            handler.post_execute(context, duration, end_time)

    def on_error(self, error: Exception, context: dict[str, Any]) -> None:
        for handler in self.handlers:
            handler.on_error(error, context)


def wrap_function[T](
    func: Callable[..., T], events: BaseRegistryEvents
) -> Callable[..., T]:
    """Wrap a function with event handling.

    Creates a wrapper that tracks execution metrics and triggers event handlers.

    Args:
        func: Function to wrap
        events: Event handler implementation

    Returns:
        Wrapped function with event handling

    Example:
        ```python
        def my_func(x: int) -> int:
            return x * 2

        events = MetricsRegistryEvents()
        wrapped = wrap_function(my_func, events)
        result = wrapped(5)  # Execution will be tracked
        ```

    Note:
        The wrapper maintains the original function's return type and signature.
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        """Execute the wrapped function with event handling.

        Args:
            *args: Positional arguments for the wrapped function
            **kwargs: Keyword arguments for the wrapped function

        Returns:
            Result from the wrapped function

        Raises:
            Exception: Any exception from the wrapped function
        """
        context = ExecutionContext(
            function_name=func.__name__,
            args=args,
            kwargs=kwargs,
            start_time=datetime.now(),
            result=None,
            error=None,
        )

        # Pre-execution
        events.pre_execute(context)

        try:
            # Execute
            result = func(*args, **kwargs)
            context = ExecutionContext(
                function_name=func.__name__,
                args=args,
                kwargs=kwargs,
                start_time=context.start_time,
                result=result,
                error=None,
            )

            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - context.start_time).total_seconds()

            # Post-execution
            events.post_execute(context, duration, end_time)
        except Exception as e:
            # Handle error
            context = ExecutionContext(
                function_name=func.__name__,
                args=args,
                kwargs=kwargs,
                start_time=context.start_time,
                error=e,
                result=None,
            )

            end_time = datetime.now()
            duration = (end_time - context.start_time).total_seconds()

            error_ctx = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
            events.on_error(e, error_ctx)
            events.post_execute(context, duration, end_time)
            raise
        else:
            return result

    return wrapper


def register_tool[T](**metadata: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to register a tool with event handling.

    Registers a function as a tool and wraps it with metrics and logging.

    Args:
        **metadata: Arbitrary keyword arguments for tool metadata

    Returns:
        Decorator function that wraps the tool

    Example:
        ```python
        @register_tool(name="calculator", group="math")
        def add(a: int, b: int) -> int:
            return a + b
        ```

    Note:
        The decorator automatically sets up both metrics and logging handlers.

    Warning:
        The logging handler writes to "function_calls.log" by default.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Create event handlers
        metrics = MetricsRegistryEvents()
        logging_handler = LoggingRegistryEvents("function_calls.log")
        events = CompositeEvents([metrics, logging_handler])

        # Register
        events.on_register(func, metadata)

        # Wrap with event handling
        return wrap_function(func, events)

    return decorator


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Create shared event handlers that we'll use for all functions
    metrics_handler = MetricsRegistryEvents()
    logging_handler = LoggingRegistryEvents("function_calls.log")
    shared_events = CompositeEvents([metrics_handler, logging_handler])

    def register_tool_with_events[T](
        **metadata: Any,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Create a tool registration decorator using shared event handlers."""

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            shared_events.on_register(func, metadata)
            return wrap_function(func, shared_events)

        return decorator

    @register_tool_with_events(name="add", group="math")
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    @register_tool_with_events(name="divide", group="math")
    def divide(a: float, b: float) -> float:
        """Divide two numbers."""
        return a / b

    # Test successful execution
    add_result = add(5.0, 3.1)
    print(f"Add result: {add_result}")

    # Test error case
    try:
        err = divide(10.0, 0.0)
    except ZeroDivisionError:
        print("Caught expected division error")

    # Show metrics using the shared metrics handler
    print("\nMetrics for add:", metrics_handler.get_metrics("add"))
    print("Metrics for divide:", metrics_handler.get_metrics("divide"))
