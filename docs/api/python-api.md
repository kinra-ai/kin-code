# Python API Reference

Integrate Kin Code into your Python applications for automation, scripting, and custom workflows.

## Overview

The Python API provides programmatic access to Kin Code's agent capabilities. Use it when you need to:

- **Automate code tasks** - CI/CD pipelines, batch processing, scheduled jobs
- **Build integrations** - Custom tools, IDE plugins, web services
- **Process at scale** - Iterate over multiple files or projects
- **Embed AI capabilities** - Add agent features to your applications

**When to use programmatic vs CLI:**

| CLI Mode | Python API |
|----------|------------|
| Interactive development | Automated workflows |
| Manual approval of tools | Auto-approved execution |
| Human-in-the-loop tasks | Batch processing |
| One-off exploration | Repeatable automation |

## Installation

Ensure Kin Code is installed in your environment:

```bash
uv add kin-code
```

## Quick Start

Minimal example to run a single prompt:

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig

# Load configuration from ~/.kin-code/config.toml
config = KinConfig.load()

# Execute a prompt
result = run_programmatic(
    config=config,
    prompt="Find all TODO comments in this project",
)

print(result)
```

That's it! The agent will execute the prompt, run tools as needed (auto-approved by default), and return the final response.

## Core Function

### run_programmatic()

The main entry point for programmatic execution.

```python
def run_programmatic(
    config: KinConfig,
    prompt: str,
    max_turns: int | None = None,
    max_price: float | None = None,
    output_format: OutputFormat = OutputFormat.TEXT,
    previous_messages: list[LLMMessage] | None = None,
    mode: AgentMode = AgentMode.AUTO_APPROVE,
) -> str | None
```

**Parameters:**

- `config` (KinConfig): Configuration object containing model, API keys, and settings
- `prompt` (str): The user prompt to process
- `max_turns` (int | None): Maximum number of LLM turns before stopping. None means unlimited.
- `max_price` (float | None): Maximum cost in USD before stopping. None means unlimited.
- `output_format` (OutputFormat): Format for output (TEXT, JSON, or STREAMING)
- `previous_messages` (list[LLMMessage] | None): Messages from a previous conversation to continue from
- `mode` (AgentMode): Operating mode (defaults to AUTO_APPROVE for automation)

**Returns:**

- `str | None`: The final assistant response text, or None if no response

**Raises:**

- `ConversationLimitException`: When max_turns or max_price limit is exceeded
- `AgentError`: For agent state or configuration errors
- `LLMResponseError`: When LLM response is malformed
- `RuntimeError`: For API errors or network issues

**Example:**

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig

config = KinConfig.load()

try:
    result = run_programmatic(
        config=config,
        prompt="List all Python files in src/",
        max_turns=5,
        max_price=0.10,
    )
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

## Configuration

### Building Configuration

Load configuration from file:

```python
from kin_code.core.config import KinConfig

# Load from ~/.kin-code/config.toml
config = KinConfig.load()

# Load with specific agent profile
config = KinConfig.load(agent="code-reviewer")

# Override settings
config = KinConfig.load(
    active_model="devstral-small",
    auto_compact_threshold=100_000,
)
```

### Creating Configuration Programmatically

```python
from kin_code.core.config import KinConfig, ModelConfig, ProviderConfig

config = KinConfig(
    active_model="devstral-2",
    models=[
        ModelConfig(
            name="kin-code-latest",
            provider="mistral",
            alias="devstral-2",
            temperature=0.2,
            input_price=0.4,
            output_price=2.0,
        )
    ],
    providers=[
        ProviderConfig(
            name="mistral",
            api_base="https://api.mistral.ai/v1",
            api_key_env_var="MISTRAL_API_KEY",
        )
    ],
    workdir="/path/to/project",
    enabled_tools=["grep", "read_file"],  # Restrict available tools
)
```

### Configuration Options

Key configuration fields:

```python
config = KinConfig(
    active_model="devstral-2",           # Model alias to use
    workdir="/path/to/project",          # Working directory for tools
    enabled_tools=["grep", "read_file"], # Whitelist specific tools
    disabled_tools=["bash"],             # Blacklist specific tools
    auto_compact_threshold=200_000,      # Token limit before auto-compaction
    api_timeout=720.0,                   # API request timeout in seconds
    include_project_context=True,        # Include project README/structure
)
```

## Basic Usage

### Single-Shot Conversations

Execute a one-time prompt:

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig

config = KinConfig.load()

result = run_programmatic(
    config=config,
    prompt="Refactor the calculate() function in utils.py",
)

if result:
    print(f"Agent response: {result}")
```

### Error Handling

Handle common exceptions:

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig, MissingAPIKeyError
from kin_code.core.utils import ConversationLimitException

try:
    config = KinConfig.load()
    result = run_programmatic(
        config=config,
        prompt="Analyze the codebase",
        max_turns=10,
        max_price=1.00,
    )
except MissingAPIKeyError as e:
    print(f"Missing API key: {e.env_key}")
    print(f"Set {e.env_key} in ~/.kin-code/.env")
except ConversationLimitException as e:
    print(f"Limit reached: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
```

## Continued Conversations

### Using Agent Directly

For multi-turn conversations, use the Agent class directly:

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode

config = KinConfig.load()
agent = Agent(
    config=config,
    mode=AgentMode.AUTO_APPROVE,
    max_turns=20,
    max_price=2.00,
)

# First conversation turn
async def main():
    async for event in agent.act("What files are in src/?"):
        pass  # Events are emitted during execution

    # Continue the conversation
    async for event in agent.act("Now check which ones have tests"):
        pass

    # Access conversation history
    print(f"Total messages: {len(agent.messages)}")
    print(f"Total cost: ${agent.stats.session_cost:.4f}")

import asyncio
asyncio.run(main())
```

### Preserving Message History

Continue a conversation using previous messages:

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.agent import Agent
from kin_code.core.modes import AgentMode

config = KinConfig.load()

# First interaction
agent = Agent(config, mode=AgentMode.AUTO_APPROVE)

async def first_interaction():
    async for event in agent.act("List Python files"):
        pass
    return agent.messages

import asyncio
messages = asyncio.run(first_interaction())

# Continue conversation with previous context
result = run_programmatic(
    config=config,
    prompt="Which of those files have tests?",
    previous_messages=messages,
)
```

**Note:** System messages in `previous_messages` are automatically filtered out.

## Operating Modes

### Mode Overview

Kin Code supports different operational modes with varying safety levels:

```python
from kin_code.core.modes import AgentMode

# DEFAULT - Interactive mode, requires approval
AgentMode.DEFAULT

# PLAN - Read-only exploration (grep, read_file, todo only)
AgentMode.PLAN

# ACCEPT_EDITS - Auto-approves file edits, prompts for other tools
AgentMode.ACCEPT_EDITS

# AUTO_APPROVE - Auto-approves all tools (recommended for automation)
AgentMode.AUTO_APPROVE
```

### Using Modes

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode

config = KinConfig.load()

# Read-only exploration
result = run_programmatic(
    config=config,
    prompt="Analyze the codebase structure",
    mode=AgentMode.PLAN,  # Only grep, read_file, todo
)

# Auto-approve all tools (default for programmatic)
result = run_programmatic(
    config=config,
    prompt="Fix the bug in main.py",
    mode=AgentMode.AUTO_APPROVE,
)
```

### Mode Properties

```python
from kin_code.core.modes import AgentMode, ModeSafety

mode = AgentMode.PLAN

print(mode.display_name)      # "Plan"
print(mode.description)       # "Read-only mode for exploration and planning"
print(mode.auto_approve)      # True
print(mode.safety)            # ModeSafety.SAFE
print(mode.config_overrides)  # {"enabled_tools": ["grep", "read_file", "todo"]}
```

## Cost & Turn Limits

### Setting Limits

Prevent runaway executions with limits:

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.utils import ConversationLimitException

config = KinConfig.load()

try:
    result = run_programmatic(
        config=config,
        prompt="Refactor the entire codebase",
        max_turns=10,      # Stop after 10 LLM calls
        max_price=0.50,    # Stop if cost exceeds $0.50
    )
except ConversationLimitException as e:
    print(f"Stopped: {e}")
```

### Monitoring Usage

Track costs and usage during execution:

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode

config = KinConfig.load()
agent = Agent(config, mode=AgentMode.AUTO_APPROVE)

async def run_with_monitoring():
    async for event in agent.act("Analyze the project"):
        pass

    stats = agent.stats
    print(f"Steps: {stats.steps}")
    print(f"Input tokens: {stats.session_prompt_tokens}")
    print(f"Output tokens: {stats.session_completion_tokens}")
    print(f"Total cost: ${stats.session_cost:.4f}")
    print(f"Tools succeeded: {stats.tool_calls_succeeded}")
    print(f"Tools failed: {stats.tool_calls_failed}")

import asyncio
asyncio.run(run_with_monitoring())
```

## Output Formats

### TEXT Format (Default)

Returns the final assistant response as plain text:

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.types import OutputFormat

config = KinConfig.load()

result = run_programmatic(
    config=config,
    prompt="Find TODO comments",
    output_format=OutputFormat.TEXT,  # Default
)

print(result)  # "I found 5 TODO comments in the following files..."
```

### JSON Format

Returns all messages as JSON at completion:

```python
import json
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.types import OutputFormat

config = KinConfig.load()

result = run_programmatic(
    config=config,
    prompt="List Python files",
    output_format=OutputFormat.JSON,
)

# Result is None - JSON is written to stdout
# To capture it, use a custom stream:

import sys
from io import StringIO
from kin_code.core.agent import Agent
from kin_code.core.modes import AgentMode
from kin_code.core.output_formatters import create_formatter

buffer = StringIO()
formatter = create_formatter(OutputFormat.JSON, stream=buffer)

agent = Agent(
    config,
    mode=AgentMode.AUTO_APPROVE,
    message_observer=formatter.on_message_added,
)

async def run():
    async for event in agent.act("List files"):
        formatter.on_event(event)
    formatter.finalize()

import asyncio
asyncio.run(run())

messages = json.loads(buffer.getvalue())
print(f"Captured {len(messages)} messages")
```

### STREAMING Format

Emits newline-delimited JSON as messages are added:

```python
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.types import OutputFormat

config = KinConfig.load()

# Each message is emitted as JSON on its own line
run_programmatic(
    config=config,
    prompt="Analyze the codebase",
    output_format=OutputFormat.STREAMING,
)
```

## Advanced Usage

### Custom Tool Configuration

Configure tool permissions programmatically:

```python
from kin_code.core.config import KinConfig, BaseToolConfig
from kin_code.core.tools.base import ToolPermission

config = KinConfig(
    active_model="devstral-2",
    tools={
        "bash": BaseToolConfig(
            permission=ToolPermission.NEVER,  # Disable bash
        ),
        "write_file": BaseToolConfig(
            permission=ToolPermission.ALWAYS,  # Auto-approve writes
            allowlist=["src/**/*.py"],         # Only allow src/ Python files
        ),
        "grep": BaseToolConfig(
            permission=ToolPermission.ALWAYS,
            denylist=["*.env", "*.key"],       # Block sensitive files
        ),
    },
)
```

### Event-Driven Processing

Process events as they occur:

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode
from kin_code.core.types import (
    AssistantEvent,
    ToolCallEvent,
    ToolResultEvent,
    CompactStartEvent,
)

config = KinConfig.load()
agent = Agent(config, mode=AgentMode.AUTO_APPROVE)

async def process_events():
    async for event in agent.act("Refactor main.py"):
        match event:
            case AssistantEvent(content=text):
                print(f"Assistant: {text}")

            case ToolCallEvent(tool_name=name, args=args):
                print(f"Calling tool: {name}")
                print(f"Arguments: {args}")

            case ToolResultEvent(tool_name=name, result=result, error=error):
                if error:
                    print(f"Tool failed: {name} - {error}")
                else:
                    print(f"Tool succeeded: {name}")

            case CompactStartEvent(current_context_tokens=tokens):
                print(f"Compacting context ({tokens} tokens)...")

import asyncio
asyncio.run(process_events())
```

### Message Observers

Observe all messages as they're added:

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode
from kin_code.core.types import LLMMessage

config = KinConfig.load()

def on_message(message: LLMMessage):
    print(f"[{message.role}] {message.content[:50]}...")

agent = Agent(
    config,
    mode=AgentMode.AUTO_APPROVE,
    message_observer=on_message,
)

async def run():
    async for event in agent.act("List files"):
        pass

import asyncio
asyncio.run(run())
```

### Switching Modes Mid-Conversation

Change mode while preserving conversation:

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode

config = KinConfig.load()
agent = Agent(config, mode=AgentMode.PLAN)

async def run():
    # Start in read-only mode
    async for event in agent.act("Analyze the codebase"):
        pass

    # Switch to allow edits
    await agent.switch_mode(AgentMode.ACCEPT_EDITS)

    async for event in agent.act("Fix the issues you found"):
        pass

import asyncio
asyncio.run(run())
```

### Custom Backend

Use a custom LLM backend:

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.llm.backend.factory import BACKEND_FACTORY
from kin_code.core.config import Backend

config = KinConfig.load()

# Get the default backend
provider = config.get_provider_for_model(config.get_active_model())
backend = BACKEND_FACTORY[provider.backend](
    provider=provider,
    timeout=config.api_timeout,
)

# Or use a custom backend implementation
# backend = MyCustomBackend(...)

agent = Agent(
    config,
    backend=backend,
)
```

## Real-World Examples

### CI/CD Code Review

```python
#!/usr/bin/env python3
"""Automated code review for CI/CD."""

import sys
from pathlib import Path
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode

def review_changes(files: list[str]) -> bool:
    """Review changed files and return True if no issues found."""
    config = KinConfig.load(
        enabled_tools=["grep", "read_file"],  # Read-only
    )

    files_str = ", ".join(files)
    prompt = f"""Review these files for:
    - Security vulnerabilities
    - Code quality issues
    - Missing tests

    Files: {files_str}

    Return 'APPROVED' if no issues, or list the issues found.
    """

    result = run_programmatic(
        config=config,
        prompt=prompt,
        mode=AgentMode.PLAN,  # Read-only mode
        max_turns=5,
    )

    return result and "APPROVED" in result

if __name__ == "__main__":
    changed_files = sys.argv[1:]
    if not changed_files:
        print("No files to review")
        sys.exit(0)

    if review_changes(changed_files):
        print("✓ Code review passed")
        sys.exit(0)
    else:
        print("✗ Code review found issues")
        sys.exit(1)
```

### Batch Documentation Generator

```python
"""Generate docstrings for multiple files."""

from pathlib import Path
from kin_code import run_programmatic
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode

def add_docstrings_to_file(file_path: Path) -> bool:
    """Add docstrings to a single file."""
    config = KinConfig.load(workdir=file_path.parent)

    prompt = f"""Add comprehensive docstrings to all functions and classes in {file_path.name}.
    Use Google-style docstrings. Only modify docstrings, don't change code logic."""

    try:
        run_programmatic(
            config=config,
            prompt=prompt,
            mode=AgentMode.ACCEPT_EDITS,  # Auto-approve file edits
            max_turns=3,
        )
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all Python files in src/."""
    project_root = Path.cwd()
    python_files = list(project_root.glob("src/**/*.py"))

    success_count = 0
    for file_path in python_files:
        print(f"Processing {file_path}...")
        if add_docstrings_to_file(file_path):
            success_count += 1

    print(f"Completed: {success_count}/{len(python_files)} files")

if __name__ == "__main__":
    main()
```

### Interactive Coding Assistant

```python
"""Custom interactive coding assistant with logging."""

import asyncio
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode
from kin_code.core.types import AssistantEvent, ToolCallEvent, ToolResultEvent

class CodingAssistant:
    def __init__(self, project_dir: str):
        config = KinConfig.load(workdir=project_dir)
        self.agent = Agent(
            config,
            mode=AgentMode.AUTO_APPROVE,
            max_price=5.00,  # Budget limit
        )

    async def chat(self, prompt: str) -> str:
        """Send a prompt and return the response."""
        response = ""

        async for event in self.agent.act(prompt):
            match event:
                case AssistantEvent(content=text):
                    response = text
                    print(f"\nAssistant: {text}")

                case ToolCallEvent(tool_name=name):
                    print(f"  → Using tool: {name}")

                case ToolResultEvent(tool_name=name, error=error):
                    if error:
                        print(f"  ✗ Tool failed: {name}")

        return response

    async def get_stats(self) -> dict:
        """Get session statistics."""
        stats = self.agent.stats
        return {
            "total_cost": stats.session_cost,
            "turns": stats.steps,
            "tokens": stats.session_total_llm_tokens,
            "tools_used": stats.tool_calls_succeeded,
        }

async def main():
    assistant = CodingAssistant("/path/to/project")

    # Multiple interactions
    await assistant.chat("What's the project structure?")
    await assistant.chat("Find all TODO comments")
    await assistant.chat("Create a test for main.py")

    # Check usage
    stats = await assistant.get_stats()
    print(f"\nSession stats:")
    print(f"  Cost: ${stats['total_cost']:.4f}")
    print(f"  Turns: {stats['turns']}")
    print(f"  Tools used: {stats['tools_used']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Scheduled Maintenance

```python
"""Weekly codebase maintenance automation."""

import asyncio
from datetime import datetime
from pathlib import Path
from kin_code import run_programmatic
from kin_code.core.config import KinConfig

async def weekly_maintenance():
    """Run weekly codebase maintenance tasks."""
    config = KinConfig.load()

    tasks = [
        "Find and update outdated TODO comments older than 30 days",
        "Check for unused imports in all Python files",
        "Update copyright year in file headers if needed",
        "Find functions with complexity > 10 and add simplification suggestions as comments",
    ]

    results = []
    for task in tasks:
        print(f"\n{'='*60}")
        print(f"Task: {task}")
        print('='*60)

        try:
            result = run_programmatic(
                config=config,
                prompt=task,
                max_turns=10,
                max_price=0.50,
            )
            results.append({"task": task, "status": "success", "result": result})
        except Exception as e:
            results.append({"task": task, "status": "failed", "error": str(e)})

    # Log results
    log_file = Path("maintenance_log.txt")
    with log_file.open("a") as f:
        f.write(f"\n\n{'='*60}\n")
        f.write(f"Maintenance run: {datetime.now()}\n")
        f.write('='*60 + "\n")
        for r in results:
            f.write(f"\nTask: {r['task']}\n")
            f.write(f"Status: {r['status']}\n")
            if r['status'] == 'success':
                f.write(f"Result: {r['result']}\n")
            else:
                f.write(f"Error: {r['error']}\n")

if __name__ == "__main__":
    asyncio.run(weekly_maintenance())
```

## Error Handling

### Exception Types

```python
from kin_code.core.agent import AgentError, AgentStateError, LLMResponseError
from kin_code.core.config import MissingAPIKeyError, MissingPromptFileError
from kin_code.core.tools.base import ToolError, ToolPermissionError
from kin_code.core.tools.manager import NoSuchToolError
from kin_code.core.utils import ConversationLimitException

# Configuration errors
try:
    config = KinConfig.load()
except MissingAPIKeyError as e:
    print(f"Set {e.env_key} for {e.provider_name}")
except MissingPromptFileError as e:
    print(f"Prompt file not found: {e.system_prompt_id}")

# Agent errors
try:
    result = run_programmatic(config, prompt="...")
except AgentStateError as e:
    print(f"Agent state error: {e}")
except LLMResponseError as e:
    print(f"Invalid LLM response: {e}")
except ConversationLimitException as e:
    print(f"Limit exceeded: {e}")

# Tool errors
except ToolError as e:
    print(f"Tool execution error: {e}")
except ToolPermissionError as e:
    print(f"Tool permission denied: {e}")
except NoSuchToolError as e:
    print(f"Tool not found: {e}")

# Network/API errors
except RuntimeError as e:
    print(f"Runtime error: {e}")
```

### Retry Logic

```python
import asyncio
from kin_code import run_programmatic
from kin_code.core.config import KinConfig

async def run_with_retry(
    config: KinConfig,
    prompt: str,
    max_retries: int = 3,
) -> str | None:
    """Run with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return run_programmatic(config, prompt)
        except RuntimeError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

    return None
```

## Type Annotations

All types are fully annotated for static analysis:

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode
from kin_code.core.types import (
    LLMMessage,
    LLMChunk,
    LLMUsage,
    AgentStats,
    AssistantEvent,
    ToolCallEvent,
    ToolResultEvent,
    OutputFormat,
    Role,
    ApprovalResponse,
)
from kin_code.core.tools.base import BaseTool, ToolPermission
```

## Best Practices

1. **Always set limits** - Use `max_turns` and `max_price` to prevent runaway costs
2. **Use appropriate modes** - PLAN for exploration, AUTO_APPROVE for automation
3. **Handle exceptions** - Wrap calls in try/except for robust automation
4. **Monitor costs** - Track `agent.stats.session_cost` for budget control
5. **Restrict tools** - Use `enabled_tools` or `disabled_tools` for safety
6. **Validate results** - Check return values and handle None responses
7. **Use async properly** - The Agent class is async, run with asyncio
8. **Clean up resources** - Agent uses context managers, use `async with` when available

## Next Steps

- [Architecture Overview](../architecture/overview.md) - Deep dive into system internals
- [Configuration Reference](../reference/config-reference.md) - All config options
- [Tool Permissions](../configuration/tool-permissions.md) - Control tool access
- [Custom Tools](../customization/custom-tools.md) - Build your own tools
- [Interactive Mode](../user-guide/interactive-mode.md) - CLI usage
