"""Synthesizer - creates final output from event stream."""

from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent

from workspaces3.memory.event_stream import EventStream


class SynthesisResult(BaseModel):
    """Final synthesized output."""

    summary: str
    key_findings: list[str] = []
    artifacts_created: list[str] = []
    next_steps: list[str] = []


class Synthesizer:
    """
    Synthesizer agent that creates final output from event stream.

    Inspired by Manus's iterative synthesis - reads all actions and observations
    to produce coherent final result.
    """

    def __init__(self, model: Any = None) -> None:
        """
        Initialize synthesizer.

        Args:
            model: LLM model for synthesis
        """
        self.agent: Agent[None, SynthesisResult] = Agent(
            model=model or "claude-3-5-sonnet-20241022",
            output_type=SynthesisResult,
            instructions=self._get_system_prompt(),
        )

    def _get_system_prompt(self) -> str:
        return """You are a synthesis agent that creates final outputs from execution logs.

Your task:
1. Read the event stream of all actions and observations
2. Understand what was accomplished
3. Identify key findings or results
4. List artifacts that were created
5. Suggest next steps if applicable

Create a clear, concise summary that captures:
- What was requested (the goal)
- What was done (the actions)
- What was achieved (the results)
- What artifacts exist (files, data, etc.)

Be specific and factual. Cite concrete observations."""

    async def synthesize(self, event_stream: EventStream, goal: str) -> SynthesisResult:
        """
        Create final synthesis from event stream.

        Args:
            event_stream: Complete event stream from task execution
            goal: Original user goal

        Returns:
            SynthesisResult with summary and findings
        """
        context = self._build_context(event_stream, goal)

        result = await self.agent.run(context)
        return result.output

    def _build_context(self, event_stream: EventStream, goal: str) -> str:
        """Build context string from event stream."""
        lines = [f"Original Goal: {goal}", "", "Execution Log:", "=" * 60, ""]

        for event in event_stream.events:
            lines.append(event.to_display_string())

        lines.append("")
        lines.append("=" * 60)
        lines.append("")
        lines.append("Based on this execution log, create a synthesis.")

        return "\n".join(lines)
