# Architecture Overview

This document describes the high-level architecture of Kin Code for developers and contributors.

## System Components

```
+------------------+
|   CLI Interface  |  (Textual UI)
+------------------+
         |
+------------------+
|   Agent Loop     |  (Core logic)
+------------------+
    |    |    |
+---+ +--+ +--+---+
|     |      |    |
v     v      v    v
Tools  LLM   Skills  MCP
      Provider
```

## Core Modules

### CLI (`kin_code/cli/`)

The command-line interface built with Textual:

- `entrypoint.py` - CLI entry point and argument parsing
- `textual_ui/` - Interactive UI components
  - `app.py` - Main application
  - `widgets/` - Custom UI widgets

### Agent Loop (`kin_code/core/agent_loop.py`)

The core execution loop that:

1. Receives user input
2. Sends to LLM provider
3. Processes tool calls
4. Returns results to user

Key responsibilities:
- Message handling
- Tool execution coordination
- Context management
- Error handling

### Tool System (`kin_code/core/tools/`)

Tools are modular capabilities:

- `manager.py` - Tool registration and discovery
- `builtins/` - Built-in tool implementations
- Each tool is a self-contained module

### Provider System (`kin_code/core/providers/`)

Abstraction layer for LLM providers:

- Unified interface for OpenAI, Anthropic, etc.
- Handles API communication
- Manages rate limiting and retries

### Skills System (`kin_code/core/skills/`)

Extensibility mechanism:

- `manager.py` - Skill loading and discovery
- Parses SKILL.md files
- Injects skill instructions into context

### Configuration (`kin_code/core/config.py`)

Configuration management:

- TOML parsing
- Environment variable handling
- Configuration merging (project + user)

## Data Flow

### User Request Flow

```
User Input
    |
    v
CLI parses input
    |
    v
Agent Loop receives message
    |
    v
Context built (history + skills + tools)
    |
    v
LLM Provider called
    |
    v
Response parsed
    |
    +---> Text response displayed
    |
    +---> Tool calls extracted
              |
              v
         Tool Manager executes
              |
              v
         Results returned to loop
              |
              v
         Continue or complete
```

### Tool Execution Flow

```
Tool Call from LLM
    |
    v
Permission check
    |
    +---> Denied: Skip or error
    |
    v
User approval (if needed)
    |
    +---> Denied: Skip
    |
    v
Tool executed
    |
    v
Result formatted
    |
    v
Returned to LLM
```

## Key Design Decisions

### Modular Tools

Tools are independent modules with:
- Clear interfaces
- No shared state
- Individual permission levels

Benefits:
- Easy to add new tools
- Easy to test
- Clear security boundaries

### Provider Abstraction

All LLM providers use a common interface:

```python
class Provider:
    async def complete(messages, tools) -> Response
```

Benefits:
- Easy to add providers
- Consistent behavior
- Provider-agnostic code

### Configuration Layering

Configuration merges:
1. Defaults
2. User config
3. Project config
4. Command-line args

Benefits:
- Sensible defaults
- Per-project customization
- CLI overrides

### Async First

The codebase uses async/await throughout:
- Non-blocking I/O
- Concurrent tool execution
- Responsive UI

## Extension Points

### Adding Tools

1. Create tool module in `core/tools/builtins/`
2. Implement tool interface
3. Register in tool manager

### Adding Providers

1. Create provider module in `core/providers/`
2. Implement provider interface
3. Register in provider factory

### Adding Skills

Skills are external:
1. Create `SKILL.md` file
2. Place in skills directory
3. Automatically discovered

## Related

- [Agent Loop](agent-loop.md)
- [Tool System](tool-system.md)
- [Provider System](provider-system.md)
