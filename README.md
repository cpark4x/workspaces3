# Workspaces3

**Autonomous AI agent that takes a prompt and delivers finished work—transparently showing every step.**

A Manus-inspired autonomous agent focused on individual productivity through verifiable, transparent task execution.

## 🎯 Core Features

### ✅ Implemented (Weeks 1-5 Complete!)

**Core Engine:**
- **Event Stream Memory**: Chronological log of all actions and observations (JSONL format)
- **Agent Loop**: Analyze → Plan → Execute → Observe cycle
- **CodeAct Architecture**: Generates and executes Python code as actions
- **Synthesizer**: Final output generation from event stream

**Tools (4 implemented):**
- **File Operations**: Read, write, list, delete files in sandboxed workspace
- **Web Search**: Tavily-powered web research capability
- **Browser Automation**: Playwright integration for web scraping and navigation
- **Code Execution**: Python sandbox for running generated code

**User Experience:**
- **Transparent UI**: Gradio-based split-screen view (Manus-style)
- **Session Replay**: Review past executions step-by-step
- **Real-time Streaming**: Watch agent work live

### 🚧 Future Enhancements

- Cloud async execution (background processing)
- Multi-agent parallel execution
- Advanced verification engine
- Mobile app

## 🏗️ Architecture

```
User Goal
    ↓
Orchestrator (coordinates everything)
    ↓
Agent Loop (iterative execution)
    ├─ Planner: Goal → Plan (3-7 steps)
    ├─ Executor: Step → Tool → Result
    └─ Observer: Result → Event Stream
         ↓
Tools (sandboxed operations)
    ├─ Filesystem: Read/write files
    ├─ CodeAct: Generate & run Python
    └─ WebSearch: Tavily API
         ↓
Event Stream Memory (session.jsonl)
    ↓
Final Result
```

## 🚀 Getting Started

### Installation

```bash
cd workspaces3

# Install dependencies
make install

# Copy environment template
cp .env.example .env

# Add your API keys to .env
# - ANTHROPIC_API_KEY (required)
# - TAVILY_API_KEY (optional, for web search)
```

### Run a Task

```bash
# Launch Web UI (Recommended - Manus-style transparent view)
python launch_ui.py
# Opens at http://localhost:7860

# OR use CLI directly
uv run python -m workspaces3.orchestrator "Create a file called hello.txt with a greeting"

# With Python execution
uv run python -m workspaces3.orchestrator "Calculate the first 10 Fibonacci numbers and save to fib.txt"

# Interactive demo (terminal-based)
python demo.py
```

### Run Tests

```bash
# All tests
make test

# Code quality checks
make check
```

## 📦 Project Structure

```
workspaces3/
├── workspaces3/          # Main package
│   ├── agent/           # Agent components
│   │   ├── loop.py      # Main execution loop
│   │   ├── planner.py   # Plan generation
│   │   └── synthesizer.py # Output synthesis
│   ├── memory/          # Memory management
│   │   └── event_stream.py # Event logging
│   ├── tools/           # Agent tools
│   │   ├── base.py      # Tool interface
│   │   ├── filesystem.py # File operations
│   │   ├── web_search.py # Tavily search
│   │   ├── browser.py   # Playwright automation
│   │   └── codeact.py   # Code generation/execution
│   ├── sandbox/         # Execution environment
│   │   └── python_executor.py # Python runner
│   └── ui/              # User interfaces
│       ├── app.py       # Main Gradio UI
│       └── replay.py    # Session replay viewer
├── tests/               # Test suite
├── demo.py             # Interactive demo
├── launch_ui.py        # Launch main UI
├── launch_replay.py    # Launch replay viewer
└── pyproject.toml      # Dependencies
```

## 🧪 Development Status

### ✅ Week 1 Complete
- [x] Event Stream memory system with JSONL persistence
- [x] Agent Loop (Analyze → Plan → Execute → Observe)
- [x] File Tool with full CRUD operations
- [x] Basic Planner using PydanticAI
- [x] Simple Orchestrator
- [x] End-to-end tests passing

### ✅ Week 2 Complete
- [x] Web Search tool (Tavily)
- [x] Python Executor (sandboxed exec)
- [x] CodeAct tool (code generation + execution)
- [x] Synthesizer for final output
- [x] All tools integrated into orchestrator
- [x] 8/8 tests passing

### ✅ Week 3 Complete
- [x] Gradio web UI with split-screen layout
- [x] Real-time event streaming to UI
- [x] Transparent execution view (Manus-style)

### ✅ Week 4 Complete
- [x] Playwright browser automation
- [x] Web scraping and navigation capabilities

### ✅ Week 5 Complete
- [x] Session replay viewer
- [x] Load and review past executions
- [x] Complete Manus feature parity achieved!

## 🎓 Key Design Principles

Following amplifier philosophy:

- **Ruthless Simplicity**: File-based memory, sequential execution, minimal abstractions
- **Bricks & Studs**: Each module (memory, planner, executor, tools) independently regeneratable
- **Transparent by Default**: Event stream shows every action/observation
- **Modular Tools**: Clean interfaces, easy to extend

## 🔧 Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **LLM** | Anthropic Claude 3.5 Sonnet | Best reasoning + code generation |
| **Framework** | PydanticAI | Structured outputs, type-safe |
| **Memory** | JSON/JSONL files | Simple, inspectable, version-controllable |
| **Code Execution** | Python exec() | MVP sandboxing (Docker later) |
| **Web Search** | Tavily API | Built for AI agents |
| **Testing** | pytest + pytest-asyncio | Standard async testing |

## 📝 Example Session

```bash
$ uv run python -m workspaces3.orchestrator "Create hello.txt with greeting"

🎯 Goal: Create hello.txt with greeting
📁 Session: 20251119_160000
📂 Workspace: ./workspaces/20251119_160000/workspace

[16:00:00] 🎯 GOAL: Create hello.txt with greeting
[16:00:01] 📋 PLAN: 1 steps
[16:00:01] ⚡ ACTION: Write greeting to file
[16:00:01] 👁️  OBSERVED: Wrote 13 characters to hello.txt...
[16:00:01] ✅ COMPLETED

============================================================
RESULT:
============================================================
Task completed successfully.

Final result:
Wrote 13 characters to hello.txt

📝 Event log: ./workspaces/20251119_160000/events.jsonl
```

## 🎯 Roadmap to Manus Feature Parity

| Feature | Status | Notes |
|---------|--------|-------|
| **Multi-step planning** | ✅ Done | PydanticAI-based planner |
| **Event stream memory** | ✅ Done | JSONL chronological log |
| **File operations** | ✅ Done | Full CRUD in workspace |
| **CodeAct execution** | ✅ Done | Python code as actions |
| **Web search** | ✅ Done | Tavily integration |
| **Transparent UI** | ✅ Done | Gradio split-screen view |
| **Browser automation** | ✅ Done | Playwright integration |
| **Session replay** | ✅ Done | Review past sessions |
| **Background execution** | 🚧 Future | Cloud async execution |
| **Multi-agent parallel** | 🚧 Future | Parallel sub-agents |

**Current Parity: ~80%** (all core features implemented!)

## 🤝 Contributing

This project follows the amplifier modular design philosophy. Each component is a "brick" with clear contracts, designed to be independently regeneratable.

See `ai_context/MODULAR_DESIGN_PHILOSOPHY.md` for details.

## 📄 License

TBD
