"""Agent Loop - Manus-inspired iterative execution cycle."""

from collections.abc import Mapping
from pathlib import Path

from workspaces3.agent.planner import Plan, Planner
from workspaces3.memory.event_stream import Event, EventStream, EventType
from workspaces3.tools.base import Tool


class AgentLoop:
    """
    Core agent loop implementing: Analyze → Plan → Execute → Observe cycle.

    Inspired by Manus architecture - one action per iteration,
    observable execution with event stream logging.
    """

    def __init__(
        self,
        planner: Planner,
        tools: Mapping[str, Tool],
        session_dir: Path,
        max_iterations: int = 20,
    ) -> None:
        """
        Initialize agent loop.

        Args:
            planner: Planner agent for creating/updating plans
            tools: Available tools mapped by name
            session_dir: Directory for session data and event stream
            max_iterations: Maximum iterations before stopping
        """
        self.planner = planner
        self.tools = tools
        self.session_dir = session_dir
        self.max_iterations = max_iterations
        self.event_stream = EventStream(session_dir)

    async def run(self, goal: str) -> str:
        """
        Execute agent loop for the given goal.

        Args:
            goal: User's goal/task description

        Returns:
            Final result/artifact
        """
        self.event_stream.append(Event(event_type=EventType.USER_GOAL, content={"goal": goal}))

        current_plan: Plan | None = None
        completed_steps: list[int] = []
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # 1. ANALYZE - Get recent context
            context = self._get_context()

            # 2. PLAN - Create or update plan
            if current_plan is None:
                self.event_stream.append(
                    Event(event_type=EventType.THOUGHT, content={"thought": "Creating initial plan..."})
                )
                current_plan = await self.planner.create_plan(goal, context)
                self.event_stream.append(
                    Event(
                        event_type=EventType.PLAN,
                        content={
                            "goal": current_plan.goal,
                            "steps": [
                                {"id": s.id, "description": s.description, "tool": s.tool} for s in current_plan.steps
                            ],
                            "reasoning": current_plan.reasoning,
                        },
                    )
                )

            # Check if all steps completed
            if len(completed_steps) >= len(current_plan.steps):
                self.event_stream.append(
                    Event(event_type=EventType.THOUGHT, content={"thought": "All steps completed. Task finished."})
                )
                self.event_stream.append(Event(event_type=EventType.COMPLETION, content={"success": True}))
                break

            # 3. EXECUTE - Execute next step
            next_step_id = len(completed_steps)
            if next_step_id >= len(current_plan.steps):
                break

            step = current_plan.steps[next_step_id]

            self.event_stream.append(
                Event(
                    event_type=EventType.ACTION,
                    content={
                        "step_id": step.id,
                        "action": step.description,
                        "tool": step.tool,
                        "inputs": step.inputs,
                    },
                )
            )

            # Execute the step
            tool = self.tools.get(step.tool)
            if not tool:
                error_msg = f"Tool not found: {step.tool}"
                self.event_stream.append(Event(event_type=EventType.ERROR, content={"error": error_msg}))
                break

            result = await tool.execute(**step.inputs)

            # 4. OBSERVE - Log result
            self.event_stream.append(
                Event(
                    event_type=EventType.OBSERVATION,
                    content={
                        "step_id": step.id,
                        "success": result.success,
                        "result": result.output,
                        "error": result.error,
                        "metadata": result.metadata,
                    },
                )
            )

            if result.success:
                completed_steps.append(step.id)
            else:
                self.event_stream.append(
                    Event(
                        event_type=EventType.ERROR,
                        content={"error": f"Step {step.id} failed: {result.error}"},
                    )
                )
                break

        if iteration >= self.max_iterations:
            self.event_stream.append(
                Event(
                    event_type=EventType.ERROR,
                    content={"error": f"Max iterations ({self.max_iterations}) reached"},
                )
            )

        return self._extract_final_result()

    def _get_context(self, limit: int = 10) -> str:
        """Get recent context from event stream for planning."""
        return self.event_stream.to_context_string(limit=limit)

    def _extract_final_result(self) -> str:
        """Extract final result from event stream."""
        observations = self.event_stream.get_by_type(EventType.OBSERVATION)

        if not observations:
            return "No results produced."

        last_obs = observations[-1]
        if last_obs.content.get("success"):
            return f"Task completed successfully.\n\nFinal result:\n{last_obs.content.get('result', 'N/A')}"
        else:
            return f"Task failed.\n\nError: {last_obs.content.get('error', 'Unknown error')}"
