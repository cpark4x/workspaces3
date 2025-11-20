"""Gradio UI for Workspaces3 - Manus-style transparent execution view."""

from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

from workspaces3.orchestrator import Orchestrator

load_dotenv()


class WorkspacesUI:
    """Gradio-based UI for Workspaces3."""

    def __init__(self) -> None:
        self.orchestrator = Orchestrator(workspace_root=Path("./ui_workspaces"))
        self.current_session_dir: Path | None = None

    async def run_task_with_streaming(self, goal: str):
        """
        Run task and yield events in real-time.

        Yields events for display in execution panel.
        """
        from datetime import datetime

        from workspaces3.agent.loop import AgentLoop
        from workspaces3.agent.planner import Planner
        from workspaces3.sandbox.python_executor import PythonExecutor
        from workspaces3.tools.codeact import CodeActTool
        from workspaces3.tools.filesystem import FileSystemTool

        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.orchestrator.workspace_root / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_dir = session_dir

        workspace_dir = session_dir / "workspace"
        workspace_dir.mkdir(exist_ok=True)

        planner = Planner()
        python_executor = PythonExecutor()

        tools = {
            "filesystem": FileSystemTool(workspace_dir),
            "codeact": CodeActTool(python_executor),
        }

        import os

        if os.getenv("TAVILY_API_KEY"):
            from workspaces3.tools.web_search import WebSearchTool

            tools["web_search"] = WebSearchTool()

        agent_loop = AgentLoop(
            planner=planner,
            tools=tools,
            session_dir=session_dir,
            max_iterations=20,
        )

        yield f"🎯 Goal: {goal}\n📁 Session: {session_id}\n📂 Workspace: {workspace_dir}\n\n"

        from workspaces3.memory.event_stream import Event, EventType

        goal_event = Event(event_type=EventType.USER_GOAL, content={"goal": goal})
        agent_loop.event_stream.append(goal_event)
        yield goal_event.to_display_string() + "\n"

        current_plan = None
        completed_steps = []
        iteration = 0

        while iteration < agent_loop.max_iterations:
            iteration += 1

            context = agent_loop._get_context()

            if current_plan is None:
                thought_event = Event(event_type=EventType.THOUGHT, content={"thought": "Creating initial plan..."})
                agent_loop.event_stream.append(thought_event)
                yield thought_event.to_display_string() + "\n"

                current_plan = await planner.create_plan(goal, context)

                plan_event = Event(
                    event_type=EventType.PLAN,
                    content={
                        "goal": current_plan.goal,
                        "steps": [
                            {"id": s.id, "description": s.description, "tool": s.tool} for s in current_plan.steps
                        ],
                        "reasoning": current_plan.reasoning,
                    },
                )
                agent_loop.event_stream.append(plan_event)
                yield plan_event.to_display_string() + "\n"

            if len(completed_steps) >= len(current_plan.steps):
                completion_event = Event(event_type=EventType.COMPLETION, content={"success": True})
                agent_loop.event_stream.append(completion_event)
                yield completion_event.to_display_string() + "\n"
                break

            next_step_id = len(completed_steps)
            if next_step_id >= len(current_plan.steps):
                break

            step = current_plan.steps[next_step_id]

            action_event = Event(
                event_type=EventType.ACTION,
                content={
                    "step_id": step.id,
                    "action": step.description,
                    "tool": step.tool,
                    "inputs": step.inputs,
                },
            )
            agent_loop.event_stream.append(action_event)
            yield action_event.to_display_string() + "\n"

            tool = agent_loop.tools.get(step.tool)
            if not tool:
                error_event = Event(event_type=EventType.ERROR, content={"error": f"Tool not found: {step.tool}"})
                agent_loop.event_stream.append(error_event)
                yield error_event.to_display_string() + "\n"
                break

            result = await tool.execute(**step.inputs)

            obs_event = Event(
                event_type=EventType.OBSERVATION,
                content={
                    "step_id": step.id,
                    "success": result.success,
                    "result": result.output,
                    "error": result.error,
                    "metadata": result.metadata,
                },
            )
            agent_loop.event_stream.append(obs_event)
            yield obs_event.to_display_string() + "\n"

            if result.success:
                completed_steps.append(step.id)
            else:
                error_event = Event(
                    event_type=EventType.ERROR, content={"error": f"Step {step.id} failed: {result.error}"}
                )
                agent_loop.event_stream.append(error_event)
                yield error_event.to_display_string() + "\n"
                break

        yield "\n" + "=" * 60 + "\n"
        yield "✅ Task Complete\n"
        yield f"📝 Event log: {session_dir / 'events.jsonl'}\n"

    def build_ui(self) -> gr.Blocks:
        """Build Gradio interface."""

        with gr.Blocks(title="Workspaces3 - Autonomous Agent") as app:
            gr.Markdown("# 🤖 Workspaces3\n**Autonomous AI Agent - Manus Competitor**")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 💬 Task Input")
                    goal_input = gr.Textbox(
                        label="What would you like me to do?",
                        placeholder="Example: Research Python async patterns and create a summary",
                        lines=3,
                    )
                    submit_btn = gr.Button("🚀 Run Task", variant="primary", size="lg")

                    gr.Markdown("### 📋 Example Tasks")
                    gr.Markdown(
                        """
                    - Create a file called hello.txt with a greeting
                    - Calculate the first 20 Fibonacci numbers
                    - Research Python async patterns
                    - Create a todo list app specification
                    """
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 🖥️ Agent Computer (Live Execution)")
                    execution_output = gr.Textbox(
                        label="",
                        lines=20,
                        max_lines=30,
                        autoscroll=True,
                        show_copy_button=True,
                        interactive=False,
                    )

            submit_btn.click(
                fn=self.run_task_with_streaming,
                inputs=[goal_input],
                outputs=[execution_output],
                show_progress="full",
            )

            gr.Markdown(
                """
            ---
            **Status**: Weeks 1-2 MVP Complete ✅
            - Event Stream Memory, Agent Loop, Planner, Tools (File, Web, CodeAct)
            - Real-time transparent execution view

            **Roadmap**: Week 4 - Browser Automation | Week 5 - Session Replay
            """
            )

        return app

    def launch(self, **kwargs) -> None:
        """Launch the Gradio app."""
        app = self.build_ui()
        app.launch(**kwargs)


def main():
    """Launch Workspaces3 UI."""
    ui = WorkspacesUI()
    ui.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()
