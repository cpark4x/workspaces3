"""Session replay - view past agent executions."""

import json
from pathlib import Path

import gradio as gr

from workspaces3.memory.event_stream import Event


class SessionReplay:
    """Replay past agent sessions."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root

    def list_sessions(self) -> list[str]:
        """List all available sessions."""
        if not self.workspace_root.exists():
            return []

        sessions = []
        for session_dir in sorted(self.workspace_root.iterdir(), reverse=True):
            if session_dir.is_dir() and (session_dir / "events.jsonl").exists():
                sessions.append(session_dir.name)

        return sessions

    def load_session(self, session_id: str) -> str:
        """Load and format session events."""
        session_dir = self.workspace_root / session_id
        events_file = session_dir / "events.jsonl"

        if not events_file.exists():
            return f"Session not found: {session_id}"

        events = []
        with open(events_file) as f:
            for line in f:
                if line.strip():
                    event_data = json.loads(line)
                    event = Event(**event_data)
                    events.append(event)

        output = [
            f"📼 Session Replay: {session_id}",
            f"📁 Location: {session_dir}",
            f"📊 Total Events: {len(events)}",
            "",
            "=" * 60,
            "",
        ]

        for event in events:
            output.append(event.to_display_string())

        output.extend(["", "=" * 60, f"✅ Session replay complete ({len(events)} events)"])

        return "\n".join(output)

    def build_ui(self) -> gr.Blocks:
        """Build session replay UI."""

        with gr.Blocks(title="Workspaces3 - Session Replay") as app:
            gr.Markdown("# 📼 Session Replay\n**Review past agent executions**")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Select Session")
                    session_dropdown = gr.Dropdown(
                        label="Available Sessions", choices=self.list_sessions(), interactive=True
                    )
                    refresh_btn = gr.Button("🔄 Refresh List")
                    load_btn = gr.Button("📼 Load Session", variant="primary")

                with gr.Column(scale=2):
                    gr.Markdown("### 🖥️ Execution Log")
                    replay_output = gr.Textbox(
                        label="", lines=25, max_lines=40, autoscroll=True, show_copy_button=True, interactive=False
                    )

            refresh_btn.click(fn=self.list_sessions, inputs=[], outputs=[session_dropdown])

            load_btn.click(fn=self.load_session, inputs=[session_dropdown], outputs=[replay_output])

        return app


def main():
    """Launch session replay viewer."""
    replay = SessionReplay(workspace_root=Path("./ui_workspaces"))
    app = replay.build_ui()
    app.launch(server_name="0.0.0.0", server_port=7861, share=False)


if __name__ == "__main__":
    main()
