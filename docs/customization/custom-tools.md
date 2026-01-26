# Custom Tools

Build your own tools in Python to extend Kin Code's capabilities.

## Overview

Custom tools let you add new capabilities to the agent. Tools are Python classes that define a schema for arguments and implement the execution logic.

## Tool Structure

A custom tool consists of:
1. **Arguments model**: Pydantic model defining input parameters
2. **Result model**: Pydantic model defining output
3. **Config model**: Optional configuration class
4. **Tool class**: The implementation

## Basic Example

```python
from pydantic import BaseModel, Field
from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
)


class CalculatorArgs(BaseModel):
    """Arguments for the calculator tool."""
    expression: str = Field(description="Mathematical expression to evaluate")


class CalculatorResult(BaseModel):
    """Result from the calculator tool."""
    result: float
    expression: str


class Calculator(BaseTool[CalculatorArgs, CalculatorResult, BaseToolConfig, BaseToolState]):
    description = "Evaluate mathematical expressions"

    async def run(self, args: CalculatorArgs) -> CalculatorResult:
        result = eval(args.expression)  # Note: Use a safe evaluator in production
        return CalculatorResult(result=result, expression=args.expression)
```

## Adding Prompts

Create a prompt file to guide the agent on when and how to use your tool:

```
my_tool/
    __init__.py
    my_tool.py
    prompts/
        my_tool.md
```

The prompt file (`prompts/my_tool.md`) should explain:
- When to use the tool
- What arguments to provide
- Expected behavior

## Installing Custom Tools

### Option 1: Tool Paths

Add directories to search in `config.toml`:

```toml
tool_paths = ["~/.kin-code/tools", "./my_project_tools"]
```

### Option 2: Package Installation

Package your tools and install them. They'll be discovered automatically if they're in the Python path.

## Custom Configuration

Tools can have custom configuration:

```python
class MyToolConfig(BaseToolConfig):
    api_endpoint: str = "https://api.example.com"
    timeout: int = 30
```

Configure in `config.toml`:

```toml
[tools.my_tool]
permission = "ask"
api_endpoint = "https://custom.endpoint.com"
timeout = 60
```

## Tool State

Tools can maintain state across invocations:

```python
class CounterState(BaseToolState):
    count: int = 0


class Counter(BaseTool[CounterArgs, CounterResult, BaseToolConfig, CounterState]):
    async def run(self, args: CounterArgs) -> CounterResult:
        self.state.count += 1
        return CounterResult(count=self.state.count)
```

## Best Practices

1. **Clear descriptions**: Help the agent know when to use your tool
2. **Typed arguments**: Use Pydantic fields with descriptions
3. **Error handling**: Raise `ToolError` for user-facing errors
4. **Async implementation**: The `run` method must be async
5. **Prompt files**: Always include a prompt explaining usage

## API Reference

See the base classes in `kin_code/core/tools/base.py`:

- `BaseTool`: Base class for all tools
- `BaseToolConfig`: Configuration with permission, allowlist, denylist
- `BaseToolState`: State maintained across invocations
- `ToolError`: Exception for tool errors
- `ToolPermission`: Permission levels (ALWAYS, ASK, NEVER)
