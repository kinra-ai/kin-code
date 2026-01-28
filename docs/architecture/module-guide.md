# Module Guide

This guide documents the Python module structure of the `kin_code` package, providing an overview of public APIs, module relationships, and programmatic usage patterns.

## Package Structure

```
kin_code/
    __init__.py              # Package root, exports KIN_ROOT and __version__
    core/                    # Core functionality
        __init__.py          # Exports run_programmatic()
        agent_loop.py        # Main agent execution loop
        config.py            # Configuration management (VibeConfig)
        middleware.py        # Conversation middleware system
        types.py             # Core type definitions
        programmatic.py      # Non-interactive execution API
        agents/              # Agent profile system
            manager.py       # AgentManager class
            models.py        # AgentProfile, AgentType
        tools/               # Tool system
            manager.py       # ToolManager class
            base.py          # BaseTool, BaseToolConfig
            builtins/        # Built-in tool implementations
            mcp.py           # MCP protocol support
        skills/              # Skills system
            manager.py       # SkillManager class
            models.py        # SkillInfo, SkillMetadata
            parser.py        # SKILL.md parsing
        llm/                 # LLM backend abstraction
            __init__.py      # Backend exports
            types.py         # BackendLike protocol
            backend/         # Backend implementations
        paths/               # Path resolution utilities
        prompts/             # System prompt management
        session/             # Session logging and management
    cli/                     # Command-line interface
        entrypoint.py        # CLI entry point
        commands.py          # Slash command system
        textual_ui/          # Textual-based interactive UI
    acp/                     # Agent Communication Protocol
    setup/                   # Setup and onboarding
```

## Public API Overview

### Core Entry Points

The main programmatic API is exported from `kin_code.core`:

```python
from kin_code.core import run_programmatic
from kin_code.core.config import VibeConfig

# Load configuration
config = VibeConfig.load()

# Run a prompt programmatically
result = run_programmatic(
    config=config,
    prompt="Explain how Python generators work",
    max_turns=10,
    max_price=0.50
)
print(result)
```

### Configuration

Configuration is managed through `VibeConfig`:

```python
from kin_code.core.config import VibeConfig, load_api_keys_from_env

# Load API keys from ~/.config/kin/.env
load_api_keys_from_env()

# Load config with TOML + env vars + defaults
config = VibeConfig.load()

# Access model settings
model = config.get_active_model()
provider = config.get_provider_for_model(model)

# Override at load time
config = VibeConfig.load(auto_approve=True, active_model="claude-opus")
```

See `VibeConfig` class docstring for detailed configuration options.

### Manager Classes

Three manager classes handle discovery and instantiation:

#### ToolManager

```python
from kin_code.core.tools.manager import ToolManager

manager = ToolManager(config_getter=lambda: config)

# List available tools
for name, tool_cls in manager.available_tools.items():
    print(f"{name}: {tool_cls.get_description()}")

# Get a tool instance
grep = manager.get("Grep")
```

#### AgentManager

```python
from kin_code.core.agents.manager import AgentManager

manager = AgentManager(
    config_getter=lambda: config,
    initial_agent="Chat"
)

# Switch agents
manager.switch_profile("Plan")

# Get effective config with agent overrides
effective = manager.config
```

#### SkillManager

```python
from kin_code.core.skills.manager import SkillManager

manager = SkillManager(config_getter=lambda: config)

# Get a skill
if (skill := manager.get_skill("docs-writer")) is not None:
    content = skill.skill_path.read_text()
```

### Middleware System

Middleware intercepts conversation turns for flow control:

```python
from kin_code.core.middleware import (
    MiddlewarePipeline,
    TurnLimitMiddleware,
    PriceLimitMiddleware,
    AutoCompactMiddleware,
)

pipeline = MiddlewarePipeline()
pipeline.add(TurnLimitMiddleware(max_turns=50))
pipeline.add(PriceLimitMiddleware(max_price=1.00))
pipeline.add(AutoCompactMiddleware(
    threshold_percent=0.9,
    max_context=200_000
))
```

See `ConversationMiddleware` protocol for implementing custom middleware.

### LLM Backend

Backends implement the `BackendLike` protocol:

```python
from kin_code.core.llm.types import BackendLike

# Backends are async context managers
async with backend as b:
    # Non-streaming
    response = await b.complete(
        model=model_config,
        messages=messages,
        temperature=0.2,
        tools=tools,
        max_tokens=4096,
        tool_choice="auto",
        extra_headers=None
    )

    # Streaming
    async for chunk in b.complete_streaming(...):
        print(chunk.message.content, end="")
```

## Module Relationships

```
                    VibeConfig
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
  ToolManager     AgentManager    SkillManager
        |               |               |
        v               v               v
    BaseTool      AgentProfile      SkillInfo
        |
        v
   Tool Execution
        |
        v
    AgentLoop  <----  MiddlewarePipeline
        |
        v
   BackendLike (LLM)
```

**Key relationships:**

1. **VibeConfig** is the central configuration, passed to all managers
2. **Managers** handle discovery and instantiation of their resources
3. **AgentLoop** orchestrates the conversation using managers and middleware
4. **BackendLike** abstracts LLM provider communication
5. **Middleware** intercepts turns for limits, compaction, and injection

## Programmatic Usage Examples

### Simple Prompt Execution

```python
from kin_code.core import run_programmatic
from kin_code.core.config import VibeConfig, load_api_keys_from_env

load_api_keys_from_env()
config = VibeConfig.load()

result = run_programmatic(config, "What is 2 + 2?")
print(result)
```

### With Conversation History

```python
from kin_code.core.types import LLMMessage, Role

# Previous messages from a session
history = [
    LLMMessage(role=Role.user, content="My name is Alice"),
    LLMMessage(role=Role.assistant, content="Hello Alice!"),
]

result = run_programmatic(
    config,
    "What's my name?",
    previous_messages=history
)
```

### Custom Agent Loop

For more control, use `AgentLoop` directly:

```python
import asyncio
from kin_code.core.agent_loop import AgentLoop
from kin_code.core.config import VibeConfig

async def main():
    config = VibeConfig.load()

    agent = AgentLoop(
        config,
        agent_name="AutoApprove",
        max_turns=20,
        enable_streaming=True
    )

    async for event in agent.act("List files in the current directory"):
        match event:
            case AssistantEvent():
                print(event.content, end="")
            case ToolResultEvent():
                print(f"[Tool: {event.tool_name}]")

asyncio.run(main())
```

## Cross-References

For detailed API documentation, see the docstrings in:

- **Configuration**: `kin_code.core.config.VibeConfig`
- **Tools**: `kin_code.core.tools.manager.ToolManager`
- **Agents**: `kin_code.core.agents.manager.AgentManager`
- **Skills**: `kin_code.core.skills.manager.SkillManager`
- **Middleware**: `kin_code.core.middleware.ConversationMiddleware`
- **Backend**: `kin_code.core.llm.types.BackendLike`

## Related Documentation

- [Architecture Overview](overview.md) - High-level system design
- [Agent Loop](agent-loop.md) - Execution loop details
- [Tool System](tool-system.md) - Tool implementation guide
- [Provider System](provider-system.md) - LLM provider integration
