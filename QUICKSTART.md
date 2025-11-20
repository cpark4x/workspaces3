# Workspaces3 Quickstart Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Set Up Environment

```bash
cd ~/amplifier/workspaces3

# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# You need at minimum: ANTHROPIC_API_KEY
```

**Get API Keys:**
- **ANTHROPIC_API_KEY** (Required): https://console.anthropic.com/
- **TAVILY_API_KEY** (Optional): https://tavily.com/ - enables web search

Edit `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
TAVILY_API_KEY=tvly-xxxxx  # Optional
```

### Step 2: Install Dependencies (if not already done)

```bash
make install
```

This installs all Python dependencies including:
- PydanticAI (for LLM orchestration)
- Gradio (for web UI)
- Playwright (for browser automation)
- Tavily (for web search)

### Step 3: Test It!

#### Option A: Web UI (Recommended - See it work like Manus!)

```bash
python launch_ui.py
```

Then:
1. Open http://localhost:7860 in your browser
2. Enter a task in the left panel
3. Click "🚀 Run Task"
4. Watch the agent work in real-time on the right panel!

**Example tasks to try:**
- "Create a file called hello.txt with a greeting"
- "Calculate the first 10 Fibonacci numbers and save to fib.txt"
- "Create a simple todo list in todo.md"

#### Option B: CLI (Quick test without UI)

```bash
uv run python -m workspaces3.orchestrator "Create a file called test.txt with 'Hello from Workspaces3!'"
```

You'll see:
```
🎯 Goal: Create a file called test.txt with 'Hello from Workspaces3!'
📁 Session: 20251119_160000
📂 Workspace: ./workspaces/20251119_160000/workspace

[16:00:00] 🎯 GOAL: Create a file called test.txt with 'Hello from Workspaces3!'
[16:00:01] 📋 PLAN: 1 steps
[16:00:01] ⚡ ACTION: Write text to file
[16:00:01] 👁️  OBSERVED: Wrote 25 characters to test.txt...
[16:00:01] ✅ COMPLETED

============================================================
RESULT:
============================================================
Task completed successfully.

Final result:
Wrote 25 characters to test.txt

📝 Event log: ./workspaces/20251119_160000/events.jsonl
```

### Step 4: Check the Results

```bash
# See the file that was created
cat workspaces/20251119_160000/workspace/test.txt

# View the event log (see everything the agent did)
cat workspaces/20251119_160000/events.jsonl
```

### Step 5: Try Session Replay

```bash
python launch_replay.py
```

Then:
1. Open http://localhost:7861
2. Select a past session from the dropdown
3. Click "📼 Load Session"
4. See the complete execution replay!

---

## 🎯 Example Tasks by Complexity

### Simple (File Operations)
```bash
uv run python -m workspaces3.orchestrator "Create a file called poem.txt with a haiku about coding"
```

### Medium (Code Execution)
```bash
uv run python -m workspaces3.orchestrator "Write Python code to calculate prime numbers up to 100 and save to primes.txt"
```

### Advanced (Web Research - requires TAVILY_API_KEY)
```bash
uv run python -m workspaces3.orchestrator "Research Python async best practices and create a summary document"
```

### Complex (Browser Automation - requires Playwright install)
```bash
# First install Playwright browsers
playwright install chromium

# Then run task
uv run python -m workspaces3.orchestrator "Go to example.com and extract the main heading"
```

---

## 🧪 Run the Test Suite

```bash
# Run all automated tests
make test

# Run code quality checks
make check
```

Should see:
```
============================== 8 passed ===============================
All checks passed!
```

---

## 🐛 Troubleshooting

### "No API key" error
- Make sure `.env` file exists
- Make sure `ANTHROPIC_API_KEY` is set
- The key should start with `sk-ant-api03-`

### "Tavily API key not set"
- Web search requires TAVILY_API_KEY
- Either add it to `.env` or tasks will skip web search
- Get free key at https://tavily.com/

### "Playwright not installed"
- Run: `playwright install chromium`
- Only needed for browser automation tasks

### UI won't launch
- Make sure port 7860 isn't in use
- Try: `lsof -ti:7860 | xargs kill` to free the port

---

## 💡 Tips

1. **Start with simple file tasks** to see how it works
2. **Use the Web UI** to watch it work in real-time
3. **Check event logs** to understand what happened
4. **Use session replay** to debug or learn from past runs
5. **Keep tasks focused** - the agent works best with clear, specific goals

---

## 📚 What to Try Next

### 1. Create a Document
```
"Create a markdown document explaining how async/await works in Python with code examples"
```

### 2. Data Analysis
```
"Create a Python script that generates a CSV with sample sales data for 10 products"
```

### 3. Research Task (needs Tavily)
```
"Research the top 3 Python web frameworks and create a comparison table"
```

### 4. Web Scraping (needs Playwright)
```
"Navigate to news.ycombinator.com and extract the top 5 post titles"
```

---

## 🎉 You're Ready!

The agent is now ready to work for you. Give it a task and watch it execute autonomously!

**Questions?** Check the main README.md or IMPLEMENTATION_LOG.md for more details.
