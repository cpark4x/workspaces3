"""Tests for filesystem tool."""

import shutil
import tempfile
from pathlib import Path

import pytest

from workspaces3.tools.filesystem import FileSystemTool


@pytest.fixture
def temp_workspace():
    """Create temporary workspace directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def fs_tool(temp_workspace):
    """Create filesystem tool instance."""
    return FileSystemTool(temp_workspace)


@pytest.mark.asyncio
async def test_write_and_read_file(fs_tool):
    """Test writing and reading a file."""
    # Write file
    write_result = await fs_tool.execute(operation="write", path="test.txt", content="Hello, World!")

    assert write_result.success
    assert "test.txt" in write_result.output

    # Read file
    read_result = await fs_tool.execute(operation="read", path="test.txt")

    assert read_result.success
    assert read_result.output == "Hello, World!"
    assert read_result.metadata["size"] == 13


@pytest.mark.asyncio
async def test_list_files(fs_tool):
    """Test listing files in directory."""
    # Create some files
    await fs_tool.execute(operation="write", path="file1.txt", content="Content 1")
    await fs_tool.execute(operation="write", path="file2.txt", content="Content 2")

    # List files
    list_result = await fs_tool.execute(operation="list", path=".")

    assert list_result.success
    assert "file1.txt" in list_result.output
    assert "file2.txt" in list_result.output
    assert list_result.metadata["count"] == 2


@pytest.mark.asyncio
async def test_file_exists(fs_tool):
    """Test checking file existence."""
    # File doesn't exist yet
    exists_result = await fs_tool.execute(operation="exists", path="missing.txt")
    assert exists_result.success
    assert not exists_result.metadata["exists"]

    # Create file
    await fs_tool.execute(operation="write", path="exists.txt", content="I exist")

    # File now exists
    exists_result = await fs_tool.execute(operation="exists", path="exists.txt")
    assert exists_result.success
    assert exists_result.metadata["exists"]


@pytest.mark.asyncio
async def test_delete_file(fs_tool):
    """Test deleting a file."""
    # Create file
    await fs_tool.execute(operation="write", path="delete_me.txt", content="Temporary")

    # Delete file
    delete_result = await fs_tool.execute(operation="delete", path="delete_me.txt")
    assert delete_result.success

    # Verify deleted
    exists_result = await fs_tool.execute(operation="exists", path="delete_me.txt")
    assert not exists_result.metadata["exists"]


@pytest.mark.asyncio
async def test_read_nonexistent_file(fs_tool):
    """Test reading file that doesn't exist."""
    read_result = await fs_tool.execute(operation="read", path="nonexistent.txt")

    assert not read_result.success
    assert "not found" in read_result.error.lower()


@pytest.mark.asyncio
async def test_invalid_operation(fs_tool):
    """Test invalid operation."""
    result = await fs_tool.execute(operation="invalid_op", path="test.txt")

    assert not result.success
    assert "unknown operation" in result.error.lower()
