# Stdio Transport

Configure MCP servers using stdio transport.

## Overview

Stdio transport runs MCP servers as local processes, communicating via stdin/stdout.

## Configuration

### Basic

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

### With Environment Variables

```toml
[[mcp_servers]]
name = "custom"
transport = "stdio"
command = "my-server"
args = ["--config", "settings.json"]
env = { "DEBUG" = "1", "LOG_LEVEL" = "info" }
```

### With Timeouts

```toml
[[mcp_servers]]
name = "slow"
transport = "stdio"
command = "slow-server"
startup_timeout_sec = 30
tool_timeout_sec = 300
```

## Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `command` | string | Command to execute |
| `args` | array | Command-line arguments |
| `env` | table | Environment variables |
| `startup_timeout_sec` | number | Time to wait for startup (default: 10) |
| `tool_timeout_sec` | number | Time to wait for tool execution (default: 60) |

## Examples

### Python Server

```toml
[[mcp_servers]]
name = "py"
transport = "stdio"
command = "python"
args = ["-m", "my_mcp_server"]
```

### Node.js Server

```toml
[[mcp_servers]]
name = "node"
transport = "stdio"
command = "npx"
args = ["my-mcp-server"]
```

### With Virtual Environment

```toml
[[mcp_servers]]
name = "venv"
transport = "stdio"
command = "/path/to/venv/bin/python"
args = ["-m", "server"]
```

## When to Use

- **Local tools** - Running on the same machine
- **Simple setup** - No network configuration needed
- **Development** - Testing MCP servers locally

## Related

- [MCP Overview](overview.md)
- [MCP Configuration](configuration.md)
- [HTTP Transport](http-transport.md)
