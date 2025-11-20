"""Demo script to test Workspaces3 with real API."""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from workspaces3.orchestrator import Orchestrator

# Load environment variables
load_dotenv()


async def main():
    """Run demo task."""

    demo_tasks = [
        "Create a file called hello.txt with the message 'Hello from Workspaces3!'",
        "Create a file called poem.txt with a short haiku about coding",
    ]

    print("🚀 Workspaces3 Demo\n")
    print("Available demo tasks:")
    for i, task in enumerate(demo_tasks, 1):
        print(f"  {i}. {task}")

    print()
    choice = input("Choose task (1-2) or enter custom goal: ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(demo_tasks):
        goal = demo_tasks[int(choice) - 1]
    else:
        goal = choice

    print()
    orchestrator = Orchestrator(workspace_root=Path("./demo_workspaces"))
    await orchestrator.run_task(goal)


if __name__ == "__main__":
    asyncio.run(main())
