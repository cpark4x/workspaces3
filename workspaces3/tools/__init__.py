"""Tools for agent to interact with the world."""

from workspaces3.tools.base import Tool, ToolResult
from workspaces3.tools.filesystem import FileSystemTool
from workspaces3.tools.web_search import WebSearchTool

__all__ = ["Tool", "ToolResult", "FileSystemTool", "WebSearchTool"]
