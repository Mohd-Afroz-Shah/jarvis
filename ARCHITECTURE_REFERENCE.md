# J1 ARCHITECTURE & CODEBASE REFERENCE

**Quick Reference for Developers**

---

## Directory Structure

```
jarvis/j1/jarvis/
│
├── app/                        # Main application code
│   ├── __init__.py
│   ├── main.py                # Interactive REPL loop
│   │
│   ├── brain.py               # ⭐ CORE: Agent loop (SEE→UNDERSTAND→ACT→VERIFY)
│   ├── llm.py                 # LLM provider abstraction
│   ├── tools.py               # Tool definitions (11 tools)
│   ├── tool_executor.py       # Execute tool calls
│   │
│   ├── actions.py             # Windows automation (PyAutoGUI)
│   ├── ui.py                  # UI automation (pywinauto)
│   │
│   ├── planning.py            # Multi-step command analysis
│   ├── deterministic.py       # Simple command fast path
│   ├── optimization.py        # Inspection caching
│   │
│   ├── config.py              # Configuration management
│   ├── security.py            # Operation validation
│   ├── logging_module.py      # JSON logging system
│   └── memory.py              # Persistent notes storage
│
├── tests/
│   ├── __init__.py
│   └── test_j1.py             # 8 unit + 3 integration tests
│
├── examples/
│   └── example_basic.py       # 7 usage examples
│
├── logs/                       # Auto-created: daily JSON logs
├── notes/                      # Auto-created: saved user notes
│
├── requirements.txt           # Python dependencies (41 packages)
├── .env                       # Configuration (user-created)
│
├── README.md                  # Quick start guide
├── IMPLEMENTATION_GUIDE.md    # Comprehensive guide
├── PHASES_COMPLETE.md         # Phase-by-phase details
├── DEPLOYMENT_CHECKLIST.md    # Deployment guide
├── COMPLETION_REPORT.md       # Verification report
└── VERIFY_ALL.py              # Verification script
```

---

## Core Module Relationships

### Data Flow

```
USER COMMAND
    ↓
main.py (interactive loop)
    ↓
brain.py:understand() 
    ├─→ deterministic.py (check if simple command)
    │    └─→ Direct action via actions.py
    │
    └─→ planning.py (analyze for multi-step)
        └─→ brain.py:execute_agent_loop()
            │
            ├─→ llm.py:ask()
            │    ├─→ Ollama (local)
            │    ├─→ Gemini (cloud)
            │    └─→ OpenAI (cloud)
            │
            ├─→ tools.py (parse tool calls)
            │
            ├─→ tool_executor.py:execute_tool()
            │    ├─→ actions.py (Windows automation)
            │    ├─→ ui.py (UI element interaction)
            │    └─→ [other tool implementations]
            │
            ├─→ security.py (validate operations)
            │
            └─→ Result → (loop back if needed)
                │
                ├─→ logging_module.py (audit log)
                ├─→ memory.py (save notes)
                └─→ Return to user
```

---

## Key Files Explained

### ⭐ brain.py (285 lines) - THE BRAIN

**Purpose**: Main agent loop implementing the SEE→UNDERSTAND→ACT→VERIFY cycle

**Key Functions**:
- `understand(command)` - Public entry point
- `execute_agent_loop(user_command, max_iterations=20)` - Main loop

**How it works**:
```python
1. Take user command
2. Build conversation history
3. Send to LLM with available tools
4. Parse LLM response for tool calls
5. Execute each tool via tool_executor
6. Feed results back to LLM
7. Loop until "complete" or error
8. Return final result
```

**Error Handling**:
- Tool failures → log + report to LLM
- LLM decides recovery action
- Max 20 iterations to prevent infinite loops

---

### llm.py (127 lines) - LLM PROVIDER

**Purpose**: Abstraction layer for multiple LLM providers

**Key Functions**:
- `ask(messages, tools=None)` - Auto-detects provider
- `ask_ollama(messages, tools)` - Ollama implementation
- `ask_gemini(messages, tools)` - Gemini implementation
- `ask_openai(messages, tools)` - OpenAI implementation
- `get_provider_info()` - Debug info

**Configuration**:
```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
# Options: "ollama", "gemini", "openai"
```

**Provider Details**:
- **Ollama**: Local, free, ~15s first response
- **Gemini**: Cloud, requires API key
- **OpenAI**: Cloud, most powerful, most expensive

---

### tools.py (165 lines) - TOOL DEFINITIONS

**Purpose**: Define 11 standardized tools with OpenAI-compatible schemas

**Tools**:
1. `open_app(app_name)` - Launch applications
2. `read_screen()` - Take screenshot
3. `read_ui()` - Inspect UI elements
4. `click_ui(name, control_type)` - Click by name
5. `type_ui(name, text)` - Type into fields
6. `tap(x, y)` - Click coordinates
7. `type_text(text)` - Type raw text
8. `press_key(key)` - Press keyboard key
9. `hotkey(*keys)` - Keyboard shortcut
10. `scroll(amount)` - Scroll screen
11. `wait(seconds)` - Wait for load

**Tool Schema**:
```python
{
    "name": "tool_name",
    "description": "What the tool does",
    "parameters": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param_name"]
    }
}
```

---

### tool_executor.py (59 lines) - EXECUTOR

**Purpose**: Map tool names to Python function implementations

**Key Functions**:
- `execute_tool(name, args)` - Execute by name
- `execute_tool_call(tool_call)` - From LLM response

**Error Handling**:
- Invalid arguments → error message
- Missing function → error message
- Tool crashes → error message + logged

---

### actions.py (139 lines) - WINDOWS AUTOMATION

**Purpose**: Low-level Windows automation using PyAutoGUI

**Functions**:
- `open_app(app_name)` - Launch via subprocess
- `read_screen()` - Screenshot (PNG bytes)
- `tap(x, y)` - Click coordinates
- `type_text(text)` - Type via keyboard
- `press_key(key)` - Press single key
- `hotkey(*keys)` - Press combination (Ctrl+S, Alt+Tab, etc)
- `scroll(amount)` - Scroll up (-) or down (+)
- `wait(seconds)` - Sleep
- `save_file(filename)` - Open Save dialog

**Notes**:
- PyAutoGUI is reliable but can be slow
- Always prefer UI automation (ui.py) when possible
- Coordinates are fragile, avoid using directly

---

### ui.py (201 lines) - UI AUTOMATION

**Purpose**: Windows UI automation via pywinauto

**Functions**:
- `get_active_ui()` - Returns dict with window + controls
- `click_ui(name, control_type)` - Click by element name
- `type_ui(name, text)` - Type into text field

**Control Types Supported**:
- Button, Edit, Text, MenuItem
- CheckBox, RadioButton, ComboBox
- List, ListItem, Tab, Hyperlink

**How it works**:
1. Get active window via pywinauto
2. Search for element by name (fuzzy match)
3. Perform action (click/type)
4. Report success/failure

**Advantages over coordinates**:
- Works on any screen resolution
- More reliable and maintainable
- Handles UI changes gracefully

---

### planning.py (98 lines) - MULTI-STEP PLANNING

**Purpose**: Analyze commands for multi-step execution

**Functions**:
- `analyze_command(command)` - Detect complexity
- `create_plan(command)` - Generate step breakdown
- `should_create_plan(command)` - Heuristic check

**Multi-Step Indicators**:
- Keywords: "then", "after", "and", "next", "save", "close"
- Long text: >100 characters
- Multiple actions

**Example**:
```
Command: "Open Notepad, write hello world, save as test.txt, close"
Analysis: Multi-step (4 actions)
Plan:
  1. Open Notepad
  2. Write "hello world"
  3. Save as test.txt
  4. Close Notepad
```

---

### deterministic.py (198 lines) - SIMPLE ACTIONS

**Purpose**: Bypass LLM for common simple commands

**Recognized Patterns**:
- "Open [app]" → launch app
- "Save" → Ctrl+S
- "Close" → Alt+F4
- "Copy" / "Paste" / "Cut" → hotkeys
- "Undo" / "Redo" → hotkeys
- "Wait [n] seconds" → sleep

**Performance Benefit**:
- Deterministic: 100ms
- LLM path: 2-3 seconds
- **Speedup: 20-30x**

**How it works**:
1. Parse command with regex patterns
2. If recognized → direct action
3. If not → fall through to LLM

---

### optimization.py (170 lines) - CACHING

**Purpose**: Avoid redundant screen/UI inspection

**Key Classes**:
- `UIState` - Cache manager with TTL
- `InspectionOptimizer` - Recommendation engine

**Features**:
- Cache last screenshot/UI dump
- 5-second TTL (configurable)
- Invalidate on certain actions
- Recommend inspection before risky actions

**Benefits**:
- Save 500-1000ms per cached read
- Reduce Ollama load
- Smoother user experience

---

### security.py (161 lines) - VALIDATION

**Purpose**: Prevent dangerous operations

**Key Functions**:
- `validate_file_operation(op, path)` - Check read/write/delete
- `validate_command(cmd)` - Check shell commands
- `validate_tool_call(tool, args)` - Tool-specific validation
- `is_path_dangerous(path)` - Detect system dirs

**Protected Areas**:
- C:\Windows
- C:\Program Files
- C:\Program Files (x86)
- C:\ProgramData
- C:\System Volume Information

**Dangerous Keywords**:
- format, delete, rm, rmdir, del
- shutdown, restart, exit
- virus, malware, exploit, crack

**Configuration Control**:
```python
ALLOW_FILE_DELETE = False        # Disable deletion
ALLOW_FILE_WRITE = True          # Allow writing
ALLOW_EXTERNAL_COMMANDS = False  # Disable shell commands
```

---

### logging_module.py (77 lines) - LOGGING

**Purpose**: Comprehensive audit logging

**Key Functions**:
- `log_command(command)` - Log user input
- `log_tool_call(tool_name, args)` - Log tool execution
- `log_tool_result(result)` - Log tool output
- `log_error(error)` - Log failures
- `log_completion(status)` - Log completion
- `write_log()` - Write to file

**Log Format**:
```json
{"timestamp": "2026-08-30T15:30:45", "type": "command", "message": "Open Notepad"}
{"timestamp": "2026-08-30T15:30:47", "type": "tool_call", "tool": "open_app", "args": {"app_name": "notepad"}}
{"timestamp": "2026-08-30T15:30:48", "type": "tool_result", "result": "success"}
```

**Log Files**:
- `logs/j1_2026-08-30.log` - Today's log
- `logs/j1_2026-08-29.log` - Yesterday's log
- Rotates daily

**Security**:
- No passwords logged
- No API keys logged
- Screenshots referenced but not logged
- Large outputs truncated (max 200 chars)

---

### memory.py (71 lines) - NOTES

**Purpose**: Persistent user notes storage

**Functions**:
- `save_note(title, content)` - Save note
- `load_note(title)` - Load note
- `list_notes()` - Show all notes

**Storage**:
- Files: `notes/[title].txt`
- Format: JSON with timestamp
- Persistent: Survives restarts

**Usage**:
```
You: Remember that my project folder is D:\projects\myproject
J1: Note saved: my-project-folder

You: What notes do I have?
J1: You have 1 note: my-project-folder
```

---

### config.py (35 lines) - CONFIGURATION

**Purpose**: Centralized settings management

**Key Settings**:
```python
LLM_PROVIDER = "ollama"              # or "gemini", "openai"
OLLAMA_MODEL = "qwen3:4b"
OLLAMA_BASE_URL = "http://localhost:11434"
MAX_TOOL_ITERATIONS = 20              # Safety limit
ALLOW_FILE_DELETE = False
ALLOW_FILE_WRITE = True
ALLOW_EXTERNAL_COMMANDS = False
LOG_DIR = "logs"
NOTES_DIR = "notes"
```

**Environment Variables**:
```bash
# Set in .env or shell
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=qwen3:4b
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...
```

---

### main.py (41 lines) - ENTRY POINT

**Purpose**: Interactive command loop

**Flow**:
```python
1. Print welcome banner
2. Loop:
   a. Print prompt "You: "
   b. Read user input
   c. Log command
   d. Call brain.understand()
   e. Print J1's response
   f. Continue loop
3. Handle Ctrl+C exit
```

---

## How to Extend J1

### Add a New Tool

**Step 1**: Define in `tools.py`
```python
{
    "name": "my_tool",
    "description": "What it does",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."}
        },
        "required": ["param1"]
    }
}
```

**Step 2**: Implement in `tool_executor.py`
```python
def tool_my_tool(param1):
    # Implementation
    return {"success": True, "result": "..."}
```

**Step 3**: Add to `TOOLS` list in `tools.py`
```python
TOOLS = [...existing..., my_new_tool_definition]
```

### Add a New LLM Provider

**Step 1**: Add implementation in `llm.py`
```python
def ask_myprovider(messages, tools=None):
    # Call your LLM API
    # Return {"message": {"content": "..."}}
```

**Step 2**: Update `ask()` function
```python
if provider == "myprovider":
    return ask_myprovider(messages, tools)
```

**Step 3**: Document in `config.py`
```python
# Options: "ollama", "gemini", "openai", "myprovider"
```

### Add a New Action

**Step 1**: Implement in `actions.py` or `ui.py`
```python
def my_action(param):
    # Do something
    return True
```

**Step 2**: Create tool in `tools.py`
```python
{
    "name": "my_action",
    "description": "Does something",
    "parameters": {...}
}
```

**Step 3**: Add executor in `tool_executor.py`
```python
def tool_my_action(param):
    return actions.my_action(param)
```

---

## Testing

### Run All Tests
```bash
cd tests
python test_j1.py --suite all
```

### Run Specific Suite
```bash
python test_j1.py --suite basic       # Tool tests
python test_j1.py --suite apps        # App tests
python test_j1.py --suite integration # Multi-step
```

### Run Examples
```bash
cd examples
python example_basic.py --all
python example_basic.py --example 1
```

### Verify System
```bash
cd d:\afroz\a_projects\jarvis\j1\jarvis
python VERIFY_ALL.py
```

---

## Debugging Tips

### Enable Verbose Logging
Check `logs/j1_YYYY-MM-DD.log` for detailed execution trace.

### Test Individual Tools
```python
from app.tool_executor import execute_tool

result = execute_tool("read_screen", {})
print(result)
```

### Test LLM Provider
```python
from app.llm import ask, get_provider_info

info = get_provider_info()
print(f"Using: {info['provider']}")

messages = [{"role": "user", "content": "Hello"}]
response = ask(messages)
print(response)
```

### Test UI Automation
```python
from app.ui import get_active_ui, click_ui

ui = get_active_ui()
print(ui)  # See available elements

click_ui("Save", "Button")  # Click Save button
```

### Test Planning
```python
from app.planning import analyze_command, create_plan

cmd = "Open Notepad, write hello, save as test.txt, close"
is_multi = analyze_command(cmd)
plan = create_plan(cmd)
print(plan)
```

---

## Performance Optimization

### Inspection Caching
The system automatically caches UI/screenshot for 5 seconds. Force refresh:
```python
from app.optimization import get_optimizer

opt = get_optimizer()
opt.invalidate_cache()  # Force fresh read
```

### Use Deterministic Path
Simple commands use the fast path:
```
"Save" → 100ms (hotkey Ctrl+S)
vs
"Please save the file" → 3000ms (LLM processing)
```

### Reduce LLM Input
Keep instructions concise. Long conversation history slows down LLM.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ollama: command not found` | Install Ollama from ollama.ai |
| `ModuleNotFoundError: No module named 'X'` | Activate venv: `.venv\Scripts\activate.ps1` |
| `Connection refused: 127.0.0.1:11434` | Start Ollama: `ollama serve` |
| Tool calls not executing | Check `logs/j1_*.log` for errors |
| UI element not found | Use `read_ui()` to inspect available elements |
| Command too slow | Check if deterministic path applies |
| File write denied | Check `ALLOW_FILE_WRITE` in config |

---

## Architecture Principles

1. **Separation of Concerns**
   - LLM logic separate from action logic
   - Tool definitions separate from execution
   - Security separate from core logic

2. **Provider Abstraction**
   - Single `ask()` interface
   - Multiple provider implementations
   - No provider-specific code in brain.py

3. **Error Recovery**
   - Tool failures → LLM decides recovery
   - No hard-coded fallbacks
   - Graceful degradation

4. **Safety First**
   - Validate all operations
   - Protect system directories
   - Log everything
   - Configurable permissions

5. **Performance**
   - Deterministic path for simple commands
   - Caching for expensive operations
   - Keyboard shortcuts over clicks
   - Minimal LLM input

6. **Testability**
   - Modular functions
   - Minimal side effects
   - Clear interfaces
   - Comprehensive test suite

---

## System Requirements

**Hardware**:
- CPU: 2+ cores
- RAM: 2GB+ (4GB+ for Ollama)
- Disk: 1GB+ (20GB+ for Ollama models)
- Network: Stable (for cloud providers)

**Software**:
- Windows 10/11
- Python 3.10+
- Ollama (for local) OR API keys (for cloud)

**Ollama Setup**:
```bash
# Install from https://ollama.ai
# Download model (one time)
ollama pull qwen3:4b

# Start service
ollama serve
```

---

## Support Resources

- **Quick Start**: README.md
- **Implementation Details**: IMPLEMENTATION_GUIDE.md
- **Phase Breakdown**: PHASES_COMPLETE.md
- **Deployment Guide**: DEPLOYMENT_CHECKLIST.md
- **Verification**: VERIFY_ALL.py
- **Tests**: tests/test_j1.py --help
- **Examples**: examples/example_basic.py --help

---

**Last Updated**: August 30, 2026  
**Version**: 1.0 Final  
**Status**: Production Ready ✅
