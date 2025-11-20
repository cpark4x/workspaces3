"""Event Stream - chronological log of all agent actions and observations."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of events in the event stream."""

    USER_GOAL = "user_goal"
    PLAN = "plan"
    ACTION = "action"
    OBSERVATION = "observation"
    THOUGHT = "thought"
    COMPLETION = "completion"
    ERROR = "error"


class Event(BaseModel):
    """A single event in the agent's execution history."""

    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: EventType
    content: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_display_string(self) -> str:
        """Format event for display in UI."""
        time_str = self.timestamp.strftime("%H:%M:%S")
        type_label = self.event_type.value.upper()

        if self.event_type == EventType.USER_GOAL:
            return f"[{time_str}] 🎯 GOAL: {self.content.get('goal', '')}"
        elif self.event_type == EventType.PLAN:
            steps = self.content.get("steps", [])
            return f"[{time_str}] 📋 PLAN: {len(steps)} steps"
        elif self.event_type == EventType.ACTION:
            action = self.content.get("action", "unknown")
            return f"[{time_str}] ⚡ ACTION: {action}"
        elif self.event_type == EventType.OBSERVATION:
            result = self.content.get("result", "")[:100]
            return f"[{time_str}] 👁️  OBSERVED: {result}..."
        elif self.event_type == EventType.THOUGHT:
            thought = self.content.get("thought", "")[:100]
            return f"[{time_str}] 💭 THINKING: {thought}..."
        elif self.event_type == EventType.COMPLETION:
            return f"[{time_str}] ✅ COMPLETED"
        elif self.event_type == EventType.ERROR:
            error = self.content.get("error", "Unknown error")
            return f"[{time_str}] ❌ ERROR: {error}"

        return f"[{time_str}] {type_label}: {self.content}"


class EventStream:
    """
    Manages the chronological event stream for an agent session.

    Inspired by Manus's event stream architecture - stores all actions,
    observations, and thoughts in append-only log.
    """

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = session_dir / "events.jsonl"
        self.events: list[Event] = []
        self._load_events()

    def _load_events(self) -> None:
        """Load existing events from disk."""
        if self.events_file.exists():
            with open(self.events_file) as f:
                for line in f:
                    if line.strip():
                        event_data = json.loads(line)
                        self.events.append(Event(**event_data))

    def append(self, event: Event) -> None:
        """Append new event to stream and persist to disk."""
        self.events.append(event)

        # Append to JSONL file
        with open(self.events_file, "a") as f:
            f.write(event.model_dump_json() + "\n")

    def get_recent(self, limit: int = 20) -> list[Event]:
        """Get most recent N events (for context window management)."""
        return self.events[-limit:] if len(self.events) > limit else self.events

    def get_by_type(self, event_type: EventType) -> list[Event]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]

    def to_context_string(self, limit: int | None = None) -> str:
        """
        Format events as context string for LLM.

        Args:
            limit: Maximum number of recent events to include (None = all)
        """
        events_to_format = self.get_recent(limit) if limit else self.events

        lines = []
        for event in events_to_format:
            lines.append(event.to_display_string())

        return "\n".join(lines)

    def get_last_observation(self) -> Event | None:
        """Get the most recent observation event."""
        observations = self.get_by_type(EventType.OBSERVATION)
        return observations[-1] if observations else None

    def has_completion(self) -> bool:
        """Check if task has been marked as complete."""
        return any(e.event_type == EventType.COMPLETION for e in self.events)

    def __len__(self) -> int:
        return len(self.events)

    def __repr__(self) -> str:
        return f"EventStream(session={self.session_dir.name}, events={len(self.events)})"
