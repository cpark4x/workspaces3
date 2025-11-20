"""Python code executor - runs code in restricted environment."""

import sys
from io import StringIO
from typing import Any


class ExecutionResult:
    """Result from Python code execution."""

    def __init__(self, success: bool, output: str, error: str | None = None, returned_value: Any = None) -> None:
        self.success = success
        self.output = output
        self.error = error
        self.returned_value = returned_value


class PythonExecutor:
    """
    Executes Python code in a restricted environment.

    For MVP: Simple exec() with captured stdout/stderr.
    Future: Add RestrictedPython or Docker sandboxing.
    """

    def __init__(self, allowed_modules: list[str] | None = None) -> None:
        """
        Initialize Python executor.

        Args:
            allowed_modules: List of allowed module names (None = all allowed in MVP)
        """
        self.allowed_modules = allowed_modules or []

    async def execute(self, code: str, globals_dict: dict[str, Any] | None = None) -> ExecutionResult:
        """
        Execute Python code and capture output.

        Args:
            code: Python code to execute
            globals_dict: Global variables to provide to the code

        Returns:
            ExecutionResult with output and any errors
        """
        if globals_dict is None:
            globals_dict = {}

        stdout_capture = StringIO()
        stderr_capture = StringIO()

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            exec(code, globals_dict)

            stdout_value = stdout_capture.getvalue()
            stderr_value = stderr_capture.getvalue()

            output = stdout_value
            if stderr_value:
                output += f"\nStderr: {stderr_value}"

            return ExecutionResult(success=True, output=output.strip(), returned_value=globals_dict.get("result"))

        except Exception as e:
            stderr_value = stderr_capture.getvalue()
            error_msg = f"{type(e).__name__}: {str(e)}"
            if stderr_value:
                error_msg += f"\nStderr: {stderr_value}"

            return ExecutionResult(success=False, output=stdout_capture.getvalue().strip(), error=error_msg)

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
