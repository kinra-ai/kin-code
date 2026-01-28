# Tools Overview

Tools are the capabilities that allow Kin Code to interact with your system. They enable reading files, executing commands, searching code, and more.

## What Are Tools?

Tools are functions the AI agent can call to perform actions. When you ask Kin Code to do something, it uses tools to accomplish the task.

For example:
```
You: "Find all TODO comments in the project"
Agent: Uses the `grep` tool to search for "TODO"
```

## Built-in Tools

Kin Code includes these built-in tools:

### File Operations

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write content to a file |
| `search_replace` | Find and replace text in files |

### Search

| Tool | Description |
|------|-------------|
| `grep` | Search files using patterns (regex supported) |

### Shell

| Tool | Description |
|------|-------------|
| `bash` | Execute shell commands |

### Task Management

| Tool | Description |
|------|-------------|
| `todo` | Manage a task list |
| `task` | Delegate work to subagents |

### User Interaction

| Tool | Description |
|------|-------------|
| `ask_user_question` | Ask clarifying questions |

### Web

| Tool | Description |
|------|-------------|
| `web_fetch` | Fetch content from URLs |
| `web_search` | Search the web |

## Tool Execution Flow

1. **Request**: You make a request
2. **Decision**: Agent decides which tool(s) to use
3. **Approval**: You approve or deny (if required)
4. **Execution**: Tool runs and returns results
5. **Response**: Agent interprets results and responds

## Tool Permissions

Each tool has a permission level:

| Permission | Behavior |
|------------|----------|
| `always` | Auto-approve, never ask |
| `ask` | Ask for approval each time |
| `never` | Always deny |

Configure in `config.toml`:

```toml
[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"
```

## MCP Tools

Additional tools can be added via MCP (Model Context Protocol) servers:

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

MCP tools are named `{server_name}_{tool_name}`.

## Enabling/Disabling Tools

### Disable Specific Tools

```toml
disabled_tools = ["bash", "write_file"]
```

### Enable Only Specific Tools

```toml
enabled_tools = ["read_file", "grep"]
```

### Pattern Matching

```toml
# Glob patterns
enabled_tools = ["read_*", "grep"]

# Regex patterns
enabled_tools = ["re:^(read|grep).*$"]
```

## Tool Output

When a tool executes, you see:
- The tool call and parameters
- The execution result
- Any errors or warnings

Toggle tool output visibility with `Ctrl+O`.

## Safety Features

1. **Approval prompts** - Review before execution
2. **Permission levels** - Control which tools auto-approve
3. **Sandboxing** - Some tools run in restricted environments
4. **Logging** - All tool calls are logged

## Tool Categories

### Safe/Read-Only

These tools don't modify anything:
- `read_file`
- `grep`
- `ask_user_question`

### Potentially Destructive

These tools can modify your system:
- `write_file`
- `search_replace`
- `bash`

Consider keeping these at `permission = "ask"`.

## Related Documentation

- [File Tools](file-tools.md)
- [Search Tools](search-tools.md)
- [Shell Tools](shell-tools.md)
- [Task Tools](task-tools.md)
- [User Interaction](user-interaction.md)
- [Web Tools](web-tools.md)
- [Tool Permissions](permissions.md)
