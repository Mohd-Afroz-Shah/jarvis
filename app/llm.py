import ollama

MODEL = "qwen3:4b"


def ask(messages, tools=None):
    options = {
        "model": MODEL,
        "messages": messages,
    }

    if tools:
        options["tools"] = tools

    return ollama.chat(**options)