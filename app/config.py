"""
Configuration Module

J1 configuration settings.
Defaults use Ollama for local LLM inference.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider Configuration
# The local server in this setup is llama.cpp's OpenAI-compatible API.
# Set LLM_PROVIDER explicitly in .env to override it.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "llamacpp")

# llama.cpp Configuration (OpenAI-compatible local API)
LLAMACPP_MODEL = os.getenv("LLAMACPP_MODEL", "Qwen/Qwen3-4B-GGUF:Q4_K_M")
LLAMACPP_BASE_URL = os.getenv("LLAMACPP_BASE_URL", "http://localhost:8080/v1")
LLAMACPP_MAX_TOKENS = int(os.getenv("LLAMACPP_MAX_TOKENS", 512))
LLAMACPP_TIMEOUT = int(os.getenv("LLAMACPP_TIMEOUT", 120))
LLAMACPP_DISABLE_THINKING = os.getenv("LLAMACPP_DISABLE_THINKING", "true").lower() == "true"

# Ollama Configuration (Optional - native Ollama API)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Gemini Configuration (Optional - Cloud)
# Retained for compatibility and explicit override.

# OpenAI Configuration (Optional - Cloud)
# Retained for compatibility and explicit override.

# J1 Configuration
MAX_TOOL_ITERATIONS = int(os.getenv("MAX_TOOL_ITERATIONS", 20))
LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
NOTES_DIR = os.path.join(os.path.dirname(__file__), "../notes")

# Security Configuration
ALLOW_FILE_DELETE = os.getenv("ALLOW_FILE_DELETE", "false").lower() == "true"
ALLOW_FILE_WRITE = os.getenv("ALLOW_FILE_WRITE", "true").lower() == "true"
ALLOW_EXTERNAL_COMMANDS = os.getenv("ALLOW_EXTERNAL_COMMANDS", "false").lower() == "true"

# Create directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(NOTES_DIR, exist_ok=True)