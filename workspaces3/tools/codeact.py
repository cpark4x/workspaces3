"""CodeAct tool - generates and executes Python code as actions."""

from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent

from workspaces3.sandbox.python_executor import PythonExecutor
from workspaces3.tools.base import Tool, ToolResult


class CodeAction(BaseModel):
    """Generated Python code action."""

    code: str
    explanation: str
    expected_output: str = ""


class CodeActTool(Tool):
    """
    CodeAct tool - Manus-inspired approach of using executable Python as actions.

    Instead of rigid JSON tool calls, generates Python code that can:
    - Combine multiple operations
    - Handle conditionals
    - Use any Python library
    """

    def __init__(self, executor: PythonExecutor, model: Any = None) -> None:
        """
        Initialize CodeAct tool.

        Args:
            executor: Python executor for running code
            model: LLM model for code generation
        """
        self.executor = executor
        self.agent: Agent[None, CodeAction] = Agent(
            model=model or "claude-3-opus-20240229",
            output_type=CodeAction,
            instructions=self._get_system_prompt(),
        )

    @property
    def name(self) -> str:
        return "codeact"

    @property
    def description(self) -> str:
        return "Generate and execute Python code to perform actions"

    def _get_system_prompt(self) -> str:
        return """You are a code generation agent that creates executable Python code.

Your task:
1. Understand the action requested
2. Generate clean, working Python code
3. Include print statements for important outputs
4. Handle errors gracefully
5. Store final result in 'result' variable if applicable

Available in context:
- Standard library modules (import as needed)
- File operations via pathlib
- HTTP requests via httpx

Output format:
- code: The Python code to execute
- explanation: Brief description of what the code does
- expected_output: What you expect the code to produce

Example:
Action: "Calculate factorial of 5"

Code:
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial of 5 is {result}")
```

Explanation: Defines recursive factorial function and calculates factorial of 5
Expected Output: "Factorial of 5 is 120"

Keep code simple and focused."""

    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Generate and execute Python code for the requested action.

        Args:
            action: Description of action to perform

        Returns:
            ToolResult with code execution output
        """
        action = kwargs.get("action")
        if not action:
            return ToolResult(success=False, output="", error="No action description provided")

        try:
            code_result = await self.agent.run(f"Action: {action}")
            code_action = code_result.output

            exec_result = await self.executor.execute(code_action.code)

            if exec_result.success:
                output = "✓ Code executed successfully\n\n"
                output += f"Explanation: {code_action.explanation}\n\n"
                output += f"Output:\n{exec_result.output}"

                return ToolResult(
                    success=True,
                    output=output,
                    metadata={
                        "code": code_action.code,
                        "explanation": code_action.explanation,
                        "execution_output": exec_result.output,
                    },
                )
            else:
                return ToolResult(
                    success=False,
                    output=exec_result.output,
                    error=f"Code execution failed: {exec_result.error}",
                    metadata={"code": code_action.code, "explanation": code_action.explanation},
                )

        except Exception as e:
            return ToolResult(success=False, output="", error=f"CodeAct failed: {str(e)}")
