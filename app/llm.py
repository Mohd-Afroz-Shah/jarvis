"""
LLM Module

Abstraction layer for different LLM providers.
Supports: Ollama (local), Gemini (Google), OpenAI
"""

import os
import json
from urllib import error, request
from config import (
    LLM_PROVIDER,
    LLAMACPP_MODEL,
    LLAMACPP_BASE_URL,
    LLAMACPP_MAX_TOKENS,
    LLAMACPP_TIMEOUT,
    LLAMACPP_DISABLE_THINKING,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
)


def ask(messages, tools=None):
    """
    Ask the LLM a question.

    Selects the configured provider but safely falls back to Ollama when a cloud
    provider is configured but its SDK is not installed.

    Args:
        messages (list): Conversation history
        tools (list): Available tools for the LLM to call

    Returns:
        dict: LLM response
    """

    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()

    if provider in ("llamacpp", "llama.cpp", "llama-cpp"):
        return ask_llamacpp(messages, tools)
    elif provider == "gemini":
        try:
            return ask_gemini(messages, tools)
        except ImportError:
            return ask_ollama(messages, tools)
    elif provider == "openai":
        try:
            return ask_openai(messages, tools)
        except ImportError:
            return ask_ollama(messages, tools)
    else:
        return ask_ollama(messages, tools)


def ask_llamacpp(messages, tools=None):
    """Query a llama.cpp server through its OpenAI-compatible HTTP API."""
    endpoint = f"{LLAMACPP_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": LLAMACPP_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": LLAMACPP_MAX_TOKENS,
    }
    if tools:
        payload["tools"] = tools
    if LLAMACPP_DISABLE_THINKING:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
        payload["reasoning_format"] = "none"

    try:
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(http_request, timeout=LLAMACPP_TIMEOUT) as response:
            completion = json.loads(response.read().decode("utf-8"))

        choice = completion.get("choices", [{}])[0]
        message = choice.get("message", {})
        return {"message": message}
    except (error.URLError, error.HTTPError, TimeoutError, ValueError) as err:
        raise RuntimeError(
            f"Failed to query llama.cpp at {endpoint}. "
            f"Is the local model server running? Error: {err}"
        ) from err


def ask_ollama(messages, tools=None):
    """Query Ollama local LLM."""
    try:
        import ollama
    except ImportError:
        raise ImportError("ollama package not installed. Install it with: pip install ollama")

    try:
        options = {
            "model": OLLAMA_MODEL,
            "messages": messages,
        }

        if tools:
            options["tools"] = tools

        # The Ollama Python client API changed across versions:
        # - older versions accepted base_url=...
        # - newer versions expect Client(host=...) and no base_url in chat()
        # Keep compatibility with both.
        if hasattr(ollama, "Client"):
            client = ollama.Client(host=OLLAMA_BASE_URL)
            response = client.chat(**options)
        else:
            response = ollama.chat(**options)

        return response

    except TypeError:
        # Fallback for older/newer API shape differences.
        try:
            if hasattr(ollama, "Client"):
                client = ollama.Client(host=OLLAMA_BASE_URL)
                response = client.chat(model=OLLAMA_MODEL, messages=messages, tools=tools or None)
                return response
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=tools or None)
            return response
        except Exception as e:
            raise RuntimeError(
                f"Failed to query Ollama at {OLLAMA_BASE_URL}. "
                f"Is Ollama running? Error: {str(e)}"
            )
    except Exception as e:
        raise RuntimeError(
            f"Failed to query Ollama at {OLLAMA_BASE_URL}. "
            f"Is Ollama running? Error: {str(e)}"
        )


def ask_gemini(messages, tools=None):
    """Query Google Gemini API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Set it in .env file.")
    
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeai not installed. Install with: pip install google-generativeai")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            gemini_messages.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Gemini doesn't support tools in the same way, so we'll process without them for now
        response = model.generate_content(gemini_messages)
        
        return {
            "message": {
                "content": response.text,
                "role": "assistant"
            }
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to query Gemini API: {str(e)}")


def ask_openai(messages, tools=None):
    """Query OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Set it in .env file.")
    
    try:
        import openai
    except ImportError:
        raise ImportError("openai not installed. Install with: pip install openai")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            tools=tools if tools else None
        )
        
        return {
            "message": {
                "content": response.choices[0].message.content,
                "role": "assistant"
            }
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to query OpenAI API: {str(e)}")


def get_provider_info():
    """Get information about the currently configured LLM provider."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    
    info = {
        "provider": provider,
        "available_providers": ["llamacpp", "ollama", "gemini", "openai"]
    }
    
    if provider in ("llamacpp", "llama.cpp", "llama-cpp"):
        info["model"] = LLAMACPP_MODEL
        info["base_url"] = LLAMACPP_BASE_URL
        info["status"] = "local"
    elif provider == "ollama":
        info["model"] = OLLAMA_MODEL
        info["base_url"] = OLLAMA_BASE_URL
        info["status"] = "local"
    elif provider == "gemini":
        info["configured"] = GEMINI_API_KEY is not None
        info["status"] = "cloud"
    elif provider == "openai":
        info["configured"] = os.getenv("OPENAI_API_KEY") is not None
        info["status"] = "cloud"
    
    return info