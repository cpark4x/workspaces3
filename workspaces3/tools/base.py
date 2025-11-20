"""Base classes for tools."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from tool execution."""

    success: bool
    output: str
    metadata: dict[str, Any] = {}
    error: str | None = None


class Tool(ABC):
    """
    Base class for all agent tools.

    Subclasses must implement: name, description, and execute()
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for identification. Must be implemented by subclass."""
        ...  # Abstract property - implemented by subclasses

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does. Must be implemented by subclass."""
        ...  # Abstract property - implemented by subclasses

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool with given parameters. Must be implemented by subclass.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with success status and output
        """
        ...  # Abstract method - implemented by subclasses

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
