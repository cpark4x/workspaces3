"""File system operations tool."""

from pathlib import Path
from typing import Any

from workspaces3.tools.base import Tool, ToolResult


class FileSystemTool(Tool):
    """Tool for reading, writing, and manipulating files."""

    def __init__(self, workspace_dir: Path) -> None:
        """
        Initialize filesystem tool.

        Args:
            workspace_dir: Root directory for file operations (sandboxed)
        """
        self.workspace_dir = workspace_dir
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "filesystem"

    @property
    def description(self) -> str:
        return "Read, write, and list files in the workspace"

    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute file operation.

        Supported operations:
        - read: Read file contents
        - write: Write content to file
        - list: List files in directory
        - delete: Delete a file
        - exists: Check if file exists

        Args:
            operation: Operation to perform (read/write/list/delete/exists)
            path: File path relative to workspace
            content: Content to write (for write operation)

        Returns:
            ToolResult with operation outcome
        """
        operation = kwargs.get("operation")
        if not operation:
            return ToolResult(
                success=False, output="", error="No operation specified. Use: read, write, list, delete, or exists"
            )

        try:
            if operation == "read":
                return await self._read_file(kwargs.get("path", ""))
            elif operation == "write":
                return await self._write_file(kwargs.get("path", ""), kwargs.get("content", ""))
            elif operation == "list":
                return await self._list_files(kwargs.get("path", "."))
            elif operation == "delete":
                return await self._delete_file(kwargs.get("path", ""))
            elif operation == "exists":
                return await self._check_exists(kwargs.get("path", ""))
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown operation: {operation}. Use: read, write, list, delete, or exists",
                )

        except Exception as e:
            return ToolResult(success=False, output="", error=f"File operation failed: {str(e)}")

    async def _read_file(self, path: str) -> ToolResult:
        """Read file contents."""
        if not path:
            return ToolResult(success=False, output="", error="No path specified for read operation")

        file_path = self.workspace_dir / path
        if not file_path.exists():
            return ToolResult(success=False, output="", error=f"File not found: {path}")

        if not file_path.is_file():
            return ToolResult(success=False, output="", error=f"Path is not a file: {path}")

        try:
            content = file_path.read_text(encoding="utf-8")
            return ToolResult(success=True, output=content, metadata={"path": str(file_path), "size": len(content)})
        except UnicodeDecodeError:
            return ToolResult(success=False, output="", error=f"File is not text (UTF-8): {path}")

    async def _write_file(self, path: str, content: str) -> ToolResult:
        """Write content to file."""
        if not path:
            return ToolResult(success=False, output="", error="No path specified for write operation")

        file_path = self.workspace_dir / path

        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")

        return ToolResult(
            success=True,
            output=f"Wrote {len(content)} characters to {path}",
            metadata={"path": str(file_path), "size": len(content)},
        )

    async def _list_files(self, path: str) -> ToolResult:
        """List files in directory."""
        dir_path = self.workspace_dir / path

        if not dir_path.exists():
            return ToolResult(success=False, output="", error=f"Directory not found: {path}")

        if not dir_path.is_dir():
            return ToolResult(success=False, output="", error=f"Path is not a directory: {path}")

        files = []
        for item in sorted(dir_path.iterdir()):
            rel_path = item.relative_to(self.workspace_dir)
            item_type = "dir" if item.is_dir() else "file"
            size = item.stat().st_size if item.is_file() else 0
            files.append({"name": item.name, "path": str(rel_path), "type": item_type, "size": size})

        output = "\n".join(f"{f['type']:4s}  {f['name']:30s}  {f['size']:>10d} bytes" for f in files)

        return ToolResult(
            success=True, output=output or "(empty directory)", metadata={"files": files, "count": len(files)}
        )

    async def _delete_file(self, path: str) -> ToolResult:
        """Delete a file."""
        if not path:
            return ToolResult(success=False, output="", error="No path specified for delete operation")

        file_path = self.workspace_dir / path

        if not file_path.exists():
            return ToolResult(success=False, output="", error=f"File not found: {path}")

        if file_path.is_dir():
            return ToolResult(success=False, output="", error=f"Cannot delete directory (use rmdir): {path}")

        file_path.unlink()

        return ToolResult(success=True, output=f"Deleted {path}", metadata={"path": str(file_path)})

    async def _check_exists(self, path: str) -> ToolResult:
        """Check if file exists."""
        if not path:
            return ToolResult(success=False, output="", error="No path specified for exists check")

        file_path = self.workspace_dir / path
        exists = file_path.exists()

        return ToolResult(
            success=True,
            output=f"{'Exists' if exists else 'Does not exist'}: {path}",
            metadata={"path": str(file_path), "exists": exists},
        )
