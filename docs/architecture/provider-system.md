# Provider System

LLM provider abstraction layer.

## Overview

The provider system provides a unified interface for different LLM providers, allowing Kin Code to work with:
- OpenAI
- Anthropic
- OpenRouter
- Local providers (Ollama, etc.)

## Architecture

```
+------------------+
|   Agent Loop     |
+------------------+
        |
        v
+------------------+
| Provider Factory |
+------------------+
        |
        v
+--------+--------+--------+
|        |        |        |
v        v        v        v
OpenAI  Anthro- OpenRo-  Local
        pic     uter
```

## Provider Interface

All providers implement a common interface:

```python
class Provider:
    async def complete(
        self,
        messages: list[Message],
        tools: list[Tool],
    ) -> Response:
        ...
```

## Provider Selection

Based on model name:
- `gpt-*` -> OpenAI provider
- `claude-*` -> Anthropic provider
- `openrouter/*` -> OpenRouter provider

## Adding Providers

1. Create provider module in `kin_code/core/providers/`
2. Implement the provider interface
3. Register in provider factory

## Configuration

Provider settings via:
- API keys in `.env`
- Model selection in `config.toml`
- Runtime override with `--model`

## Related

- [Architecture Overview](overview.md)
- [Models](../configuration/models.md)
