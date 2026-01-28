# Tool System

How tools are defined, registered, and executed.

## Overview

Tools are modular capabilities that the agent can invoke. Each tool:
- Has a defined interface
- Accepts parameters
- Returns results
- Has permission settings

## Tool Structure

Each tool is a module with:

```python
# Tool metadata
name = "tool_name"
description = "What the tool does"
parameters = {
    "param1": {"type": "string", "description": "..."},
}

# Tool implementation
async def execute(param1: str) -> str:
    # Do something
    return result
```

## Registration

Tools are registered with the Tool Manager:

1. Built-in tools are auto-registered
2. MCP tools are discovered from servers
3. Custom tools can be added

## Execution Flow

```
Tool Call from LLM
       |
       v
  Tool Manager
       |
       v
  Permission Check
       |
       +---> Denied: Return error
       |
       v
  User Approval (if needed)
       |
       +---> Denied: Return skip
       |
       v
  Execute Tool
       |
       v
  Format Result
       |
       v
  Return to Agent Loop
```

## Adding Tools

### Built-in Tools

Add to `kin_code/core/tools/builtins/`:

1. Create `my_tool.py`
2. Define metadata and execute function
3. Register in `__init__.py`

### MCP Tools

Configure MCP servers - tools are discovered automatically.

## Tool Schema

Tools expose a JSON Schema for parameters:

```json
{
  "name": "grep",
  "description": "Search files",
  "parameters": {
    "type": "object",
    "properties": {
      "pattern": {
        "type": "string",
        "description": "Search pattern"
      }
    },
    "required": ["pattern"]
  }
}
```

## Related

- [Architecture Overview](overview.md)
- [Tools Overview](../tools/overview.md)
