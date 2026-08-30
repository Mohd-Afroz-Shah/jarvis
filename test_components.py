"""
Quick test of J1 components
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

print("Testing J1 Components...")
print("="*60)

# Test 1: Import all modules
print("\n1. Testing imports...")
try:
    from config import LLM_PROVIDER, OLLAMA_MODEL
    print(f"   ✓ config.py (Provider: {LLM_PROVIDER}, Model: {OLLAMA_MODEL})")
except Exception as e:
    print(f"   ✗ config.py: {e}")

try:
    from llm import ask
    print(f"   ✓ llm.py")
except Exception as e:
    print(f"   ✗ llm.py: {e}")

try:
    from tools import TOOLS
    print(f"   ✓ tools.py ({len(TOOLS)} tools available)")
except Exception as e:
    print(f"   ✗ tools.py: {e}")

try:
    from tool_executor import execute_tool
    print(f"   ✓ tool_executor.py")
except Exception as e:
    print(f"   ✗ tool_executor.py: {e}")

try:
    from brain import understand
    print(f"   ✓ brain.py")
except Exception as e:
    print(f"   ✗ brain.py: {e}")

try:
    from logging_module import log_command
    print(f"   ✓ logging_module.py")
except Exception as e:
    print(f"   ✗ logging_module.py: {e}")

try:
    from memory import save_note, load_note
    print(f"   ✓ memory.py")
except Exception as e:
    print(f"   ✗ memory.py: {e}")

print("\n2. Testing tool executor...")
try:
    # Test opening an app
    result = execute_tool("open_app", {"app_name": "notepad"})
    print(f"   ✓ execute_tool('open_app', 'notepad'): {result[:50]}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n3. Testing screen capture...")
try:
    from actions import read_screen
    screenshot = read_screen()
    print(f"   ✓ read_screen() returned {len(screenshot)} bytes")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("Component tests complete!")
