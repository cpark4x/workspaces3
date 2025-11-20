"""Main orchestrator - coordinates all components."""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from workspaces3.agent.loop import AgentLoop
from workspaces3.agent.planner import Planner
from workspaces3.tools.filesystem import FileSystemTool


class Orchestrator:
    """
    Main orchestrator for Workspaces3.

    Coordinates planner, agent loop, tools, and memory.
    """

    def __init__(self, workspace_root: Path | None = None) -> None:
        """
        Initialize orchestrator.

        Args:
            workspace_root: Root directory for all workspaces (default: ./workspaces)
        """
        self.workspace_root = workspace_root or Path("./workspaces")
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    async def run_task(self, goal: str) -> str:
        """
        Run a task from goal to completion.

        Args:
            goal: User's goal description

        Returns:
            Final result
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.workspace_root / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        workspace_dir = session_dir / "workspace"
        workspace_dir.mkdir(exist_ok=True)

        from workspaces3.sandbox.python_executor import PythonExecutor
        from workspaces3.tools.browser import BrowserTool
        from workspaces3.tools.codeact import CodeActTool
        from workspaces3.tools.web_search import WebSearchTool

        planner = Planner()
        python_executor = PythonExecutor()

        tools = {
            "filesystem": FileSystemTool(workspace_dir),
            "codeact": CodeActTool(python_executor),
            "browser": BrowserTool(headless=True),
        }

        if os.getenv("TAVILY_API_KEY"):
            tools["web_search"] = WebSearchTool()

        agent_loop = AgentLoop(
            planner=planner,
            tools=tools,
            session_dir=session_dir,
            max_iterations=20,
        )

        print(f"🎯 Goal: {goal}")
        print(f"📁 Session: {session_id}")
        print(f"📂 Workspace: {workspace_dir}")
        print()

        result = await agent_loop.run(goal)

        print()
        print("=" * 60)
        print("RESULT:")
        print("=" * 60)
        print(result)
        print()
        print(f"📝 Event log: {session_dir / 'events.jsonl'}")

        return result


async def main() -> None:
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m workspaces3.orchestrator '<goal>'")
        print()
        print("Example:")
        print('  python -m workspaces3.orchestrator "Create a file called hello.txt with greeting"')
        sys.exit(1)

    goal = sys.argv[1]

    orchestrator = Orchestrator()
    await orchestrator.run_task(goal)


if __name__ == "__main__":
    asyncio.run(main())
