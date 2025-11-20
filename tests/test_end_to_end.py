"""End-to-end test of agent loop."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from pydantic_ai.models.test import TestModel

from workspaces3.agent.loop import AgentLoop
from workspaces3.agent.planner import Plan, Planner, Step
from workspaces3.tools.filesystem import FileSystemTool


@pytest.fixture
def temp_session_dir():
    """Create temporary session directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_workspace():
    """Create temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.asyncio
async def test_simple_file_task_end_to_end(temp_session_dir, temp_workspace):
    """Test complete agent loop with file operations."""

    mock_plan = Plan(
        goal="Create a file called greeting.txt with 'Hello, World!'",
        steps=[
            Step(
                id=0,
                description="Write greeting to file",
                tool="filesystem",
                inputs={"operation": "write", "path": "greeting.txt", "content": "Hello, World!"},
            )
        ],
        reasoning="Simple file write operation",
    )

    test_model = TestModel()
    planner = Planner(model=test_model)

    with patch.object(planner, "create_plan", new_callable=AsyncMock) as mock_create_plan:
        mock_create_plan.return_value = mock_plan

        tools = {"filesystem": FileSystemTool(temp_workspace)}

        agent_loop = AgentLoop(
            planner=planner,
            tools=tools,
            session_dir=temp_session_dir,
            max_iterations=5,
        )

        result = await agent_loop.run("Create a file called greeting.txt with 'Hello, World!'")

        assert "success" in result.lower()

        greeting_file = temp_workspace / "greeting.txt"
        assert greeting_file.exists()
        assert greeting_file.read_text() == "Hello, World!"

        assert len(agent_loop.event_stream) > 0

        events_file = temp_session_dir / "events.jsonl"
        assert events_file.exists()


@pytest.mark.asyncio
async def test_multi_step_task(temp_session_dir, temp_workspace):
    """Test agent loop with multiple steps."""

    mock_plan = Plan(
        goal="Create data.txt with 'test data', then create summary.txt",
        steps=[
            Step(
                id=0,
                description="Write test data to data.txt",
                tool="filesystem",
                inputs={"operation": "write", "path": "data.txt", "content": "test data"},
            ),
            Step(
                id=1,
                description="Create summary file",
                tool="filesystem",
                inputs={"operation": "write", "path": "summary.txt", "content": "Summary: Created data.txt"},
            ),
        ],
        reasoning="Two-step file creation",
    )

    test_model = TestModel()
    planner = Planner(model=test_model)

    with patch.object(planner, "create_plan", new_callable=AsyncMock) as mock_create_plan:
        mock_create_plan.return_value = mock_plan

        tools = {"filesystem": FileSystemTool(temp_workspace)}

        agent_loop = AgentLoop(
            planner=planner,
            tools=tools,
            session_dir=temp_session_dir,
            max_iterations=10,
        )

        result = await agent_loop.run("Create data.txt with 'test data', then create summary.txt")

        assert "success" in result.lower()

        assert (temp_workspace / "data.txt").exists()
        assert (temp_workspace / "summary.txt").exists()

        assert (temp_workspace / "data.txt").read_text() == "test data"
        assert "Summary" in (temp_workspace / "summary.txt").read_text()
