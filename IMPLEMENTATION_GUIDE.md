# J1 - Windows AI Computer Control Agent

A sophisticated Windows AI agent that understands natural language commands and performs computer control tasks autonomously. Built with local LLM support (Ollama) and extensible for cloud providers (Gemini, OpenAI).

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Windows OS
- Ollama (for local LLM) - [Download](https://ollama.ai)
- Qwen3:4B model - `ollama pull qwen3:4b`

### Installation

```bash
# Clone the repository
git clone https://github.com/Mohd-Afroz-Shah/jarvis.git
cd jarvis/j1/jarvis

# Create virtual environment
python -m venv .venv

# Activate venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create or edit `.env` file:

```env
# LLM Provider (ollama, gemini, openai)
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Gemini API Key
# GEMINI_API_KEY=your-key-here

# Optional: OpenAI API Key
# OPENAI_API_KEY=your-key-here

# Security Settings
ALLOW_FILE_DELETE=false
ALLOW_FILE_WRITE=true
ALLOW_EXTERNAL_COMMANDS=false
```

### Running J1

```bash
# Activate venv first
.venv\Scripts\activate

# Start Ollama in another terminal
ollama serve

# Run J1 in main terminal
cd app
python main.py
```

Then type natural language commands:
```
You: Open Notepad
You: Read my screen
You: Open Notepad, write hello, save as test.txt, close Notepad
```

## 📋 Features

### ✅ Implemented (Phases 1-3, 14-17, 20-21)

- **LLM Abstraction** - Switch between Ollama, Gemini, OpenAI without code changes
- **Tool System** - 11 tools for computer control
- **Tool Executor** - Maps LLM calls to Python functions
- **Agent Loop** - Complete SEE → UNDERSTAND → ACT → VERIFY cycle
- **Error Recovery** - Graceful handling of tool failures
- **Loop Protection** - Max iterations and repeated call detection
- **Logging System** - JSON-based per-day logs
- **Memory System** - Simple persistent note storage
- **Configuration** - Environment-based settings
- **Security Module** - Prevents dangerous operations
- **Multi-Provider Support** - Ollama, Gemini, OpenAI

### 🔄 Available Tools

1. **open_app** - Open applications (notepad, chrome, calculator, explorer)
2. **read_screen** - Capture and inspect current screen
3. **read_ui** - Get structured UI element information
4. **click_ui** - Click UI elements by name
5. **type_ui** - Type into text fields by name
6. **tap** - Click coordinates on screen
7. **type_text** - Type raw text
8. **press_key** - Press individual keyboard keys
9. **hotkey** - Press keyboard shortcuts (Ctrl+S, Alt+F4, etc.)
10. **scroll** - Scroll the screen
11. **wait** - Wait for applications to respond

## 📂 Project Structure

```
jarvis/j1/jarvis/
├── app/
│   ├── main.py              # Entry point
│   ├── brain.py             # Agent loop engine
│   ├── llm.py               # LLM abstraction layer
│   ├── tools.py             # Tool definitions
│   ├── tool_executor.py     # Execute tool calls
│   ├── actions.py           # Low-level Windows actions
│   ├── ui.py                # UI automation (pywinauto)
│   ├── config.py            # Configuration
│   ├── logging_module.py    # Logging system
│   ├── memory.py            # Persistent notes
│   ├── security.py          # Security validation
│   ├── planning.py          # Multi-step planning
│   ├── optimization.py      # Inspection optimization
│   ├── deterministic.py     # Simple deterministic actions
│   └── __init__.py
├── tests/
│   └── test_j1.py           # Integration test suite
├── examples/
│   └── example_basic.py     # Usage examples
├── logs/                    # Daily log files (auto-created)
├── notes/                   # Saved notes (auto-created)
├── .env                     # Configuration (create your own)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎯 Core Architecture

```
User Input (Natural Language)
    ↓
[main.py] User Input Loop
    ↓
[brain.py] Agent Loop
    ├─ Check for deterministic action
    ├─ Send to LLM with available tools
    ├─ Parse tool calls
    └─ Loop until completion
    ↓
[llm.py] LLM Provider (Ollama/Gemini/OpenAI)
    ↓
[tool_executor.py] Execute Tool
    ↓
[tools.py] Tool Wrappers
    ↓
[actions.py] Windows Actions (PyAutoGUI)
[ui.py] UI Automation (pywinauto)
    ↓
Windows OS
```

## 📖 Usage Examples

### Example 1: Open an Application
```
You: Open Notepad
```

### Example 2: Read the Screen
```
You: What's on my screen? Describe what you see.
```

### Example 3: Multi-Step Task
```
You: Open Notepad, write 'Hello World', save it as hello.txt, then close Notepad
```

### Example 4: Interactive Session
```
You: Open Calculator
You: Add 5 and 3
You: Close Calculator
```

## 🧪 Testing

### Run Component Tests
```bash
cd app
python test_components.py
```

### Run Test Suite
```bash
cd tests
python test_j1.py --suite basic        # Basic tool tests
python test_j1.py --suite apps         # Application tests
python test_j1.py --suite integration  # Multi-step tests
python test_j1.py --suite all          # All tests
```

### Run Examples
```bash
python examples/example_basic.py --example 1      # Run example 1
python examples/example_basic.py --all            # Run all examples
python examples/example_basic.py --all --pause    # Run with pauses
```

## 🔐 Security

J1 implements several security measures:

1. **File Operation Validation** - Blocks deletion/writing to system directories
2. **Command Validation** - Prevents dangerous keywords in commands
3. **Tool Validation** - Each tool call is validated before execution
4. **Logging** - All operations are logged for audit trails
5. **Configuration-based Controls** - Can disable file operations, external commands

### Security Settings (in .env)
- `ALLOW_FILE_DELETE` - Enable/disable file deletion (default: false)
- `ALLOW_FILE_WRITE` - Enable/disable file writing (default: true)
- `ALLOW_EXTERNAL_COMMANDS` - Enable/disable shell commands (default: false)

## 🚗 Performance Optimizations

1. **Deterministic Actions** - Simple commands bypass the LLM
2. **Inspection Caching** - Avoids redundant screen/UI reads
3. **Efficient Tool Selection** - LLM prefers UI automation over coordinates
4. **Keyboard Shortcuts** - Uses hotkeys for common operations

## 🔧 Advanced Configuration

### Switch to Gemini
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
```

### Switch to OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
```

### Increase Tool Iterations
```env
MAX_TOOL_ITERATIONS=30
```

## 📝 Logging

Logs are stored in `logs/j1_YYYY-MM-DD.log` in JSON format.

Each log entry contains:
- Timestamp
- Event type (command, tool_call, tool_result, error)
- Details (command text, tool name, result)

Example:
```json
{"timestamp": "2024-08-30T10:30:45.123456", "event": "command", "command": "Open Notepad"}
{"timestamp": "2024-08-30T10:30:45.234567", "event": "tool_call", "tool_name": "open_app", "tool_args": {"app_name": "notepad"}}
{"timestamp": "2024-08-30T10:30:46.345678", "event": "tool_result", "tool_name": "open_app", "result": "Successfully opened notepad."}
```

## 💾 Memory/Notes

Save notes for later reference:

From code:
```python
from memory import save_note, load_note

save_note("My Project", "My project is at D:\\projects\\myproject")
note = load_note("My Project")
```

Programmatically, J1 stores notes in `notes/` directory as `.txt` files.

## 🐛 Troubleshooting

### "Ollama not found" Error
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull the model
ollama pull qwen3:4b
```

### Import Errors
```bash
# Ensure venv is activated
.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### pywinauto Issues (Windows 10/11)
```bash
# Update pywinauto
pip install --upgrade pywinauto

# May need to install extras
pip install pywinauto[uia]
```

## 📚 Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1-3 | ✅ | LLM abstraction, tool system, executor |
| 4-8 | ✅ | Computer control, UI automation, agent loop |
| 9 | ✅ | Multi-step command planning |
| 10 | ✅ | Inspection optimization |
| 14-17 | ✅ | Memory, logging, configuration |
| 18-19 | ✅ | Performance, deterministic actions |
| 20-21 | ✅ | Model switching, security |
| 22-23 | ✅ | Testing framework, integration tests |

## 🚀 Roadmap

**Immediate (Ready Now):**
- ✅ Computer control agent with Ollama
- ✅ Multi-provider support (Gemini, OpenAI)
- ✅ Comprehensive testing

**Future Enhancements:**
- Voice input/output
- Advanced screen vision (OCR, object detection)
- Autonomous background operation
- Advanced long-term memory
- Web browsing agent
- Multi-agent architecture

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better tool call parsing from different LLM providers
- Enhanced UI detection and element identification
- Performance optimizations
- Additional tool implementations
- Better error recovery strategies

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

Built with:
- [Ollama](https://ollama.ai) - Local LLM inference
- [pyautogui](https://pyautogui.readthedocs.io) - Mouse/keyboard automation
- [pywinauto](https://pywinauto.readthedocs.io) - Windows UI automation
- [Pillow](https://pillow.readthedocs.io) - Image processing

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**J1: Making Windows computer control autonomous, reliable, and accessible.**
