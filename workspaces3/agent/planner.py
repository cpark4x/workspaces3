"""Planner - decomposes goals into executable steps."""

from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel


class Step(BaseModel):
    """A single step in the execution plan."""

    id: int
    description: str
    tool: str
    inputs: dict[str, Any] = Field(default_factory=dict)


class Plan(BaseModel):
    """Execution plan with ordered steps."""

    goal: str
    steps: list[Step]
    reasoning: str = ""


class Planner:
    """
    Planner agent that breaks down goals into executable steps.

    Inspired by Manus's planning module - decomposes complex objectives
    into ordered steps with status tracking.
    """

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", model: Any = None) -> None:
        if model is None:
            self.model = AnthropicModel(model_name)
        else:
            self.model = model
        self.agent: Agent[None, Plan] = Agent(
            model=self.model,
            output_type=Plan,
            instructions=self._get_system_prompt(),
        )

    def _get_system_prompt(self) -> str:
        return """You are a planning agent that breaks down user goals into concrete, executable steps.

Available tools:
- filesystem: Read, write, list, delete files
  Operations: read, write, list, delete, exists
- web_search: Search the web for information
  Inputs: query, max_results (optional)
- codeact: Generate and execute Python code
  Inputs: action (description of what to do)

Your task:
1. Analyze the user's goal
2. Break it into 3-7 concrete steps
3. Each step should use ONE tool with clear inputs
4. Steps should be sequential and logical
5. Keep steps simple and focused

Output a plan with:
- goal: The user's original goal
- steps: List of executable steps with tool and inputs
- reasoning: Brief explanation of your approach

Example:
Goal: "Read data.txt and create a summary in summary.txt"

Plan:
- Step 1: Read data.txt using filesystem tool
- Step 2: Analyze content and extract key points
- Step 3: Write summary to summary.txt using filesystem tool

Keep it simple. Focus on ACTIONABLE steps."""

    async def create_plan(self, goal: str, context: str = "") -> Plan:
        """
        Create an execution plan for the given goal.

        Args:
            goal: User's goal/task description
            context: Optional context from previous actions

        Returns:
            Plan with ordered steps
        """
        prompt = f"Goal: {goal}"
        if context:
            prompt += f"\n\nContext from previous actions:\n{context}"

        result = await self.agent.run(prompt)
        return result.output

    async def update_plan(self, current_plan: Plan, observation: str, completed_steps: list[int]) -> Plan:
        """
        Update plan based on observations from execution.

        Args:
            current_plan: Current execution plan
            observation: Observation from last executed step
            completed_steps: IDs of completed steps

        Returns:
            Updated plan (may add/remove/modify steps)
        """
        prompt = f"""Current plan:
Goal: {current_plan.goal}
Steps: {len(current_plan.steps)} total
Completed: {completed_steps}

Last observation: {observation}

Based on this observation, should we:
1. Continue with remaining steps as-is?
2. Add new steps?
3. Modify remaining steps?
4. Mark task as complete?

Update the plan accordingly."""

        result = await self.agent.run(prompt)
        return result.output
