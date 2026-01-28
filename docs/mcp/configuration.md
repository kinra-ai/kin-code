# MCP Configuration

Configure MCP servers in `config.toml`.

## Basic Configuration

```toml
[[mcp_servers]]
name = "my-server"
transport = "stdio"
command = "my-server-command"
```

## Configuration Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Server identifier (used in tool names) |
| `transport` | string | `"stdio"`, `"http"`, or `"streamable-http"` |

### Stdio Transport

| Field | Type | Description |
|-------|------|-------------|
| `command` | string | Command to execute |
| `args` | array | Command arguments |
| `env` | table | Environment variables |

### HTTP Transport

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Server URL |
| `headers` | table | HTTP headers |
| `api_key_env` | string | Env var containing API key |
| `api_key_header` | string | Header name for API key |
| `api_key_format` | string | Format string (e.g., `"Bearer {token}"`) |

### Timeouts

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `startup_timeout_sec` | number | 10 | Server startup timeout |
| `tool_timeout_sec` | number | 60 | Tool execution timeout |

## Examples

### Stdio Server

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
env = { "LOG_LEVEL" = "info" }
```

### HTTP Server

```toml
[[mcp_servers]]
name = "api"
transport = "http"
url = "http://localhost:8000"
headers = { "X-Custom" = "value" }
```

### With Authentication

```toml
[[mcp_servers]]
name = "secure"
transport = "http"
url = "https://api.example.com"
api_key_env = "MY_API_KEY"
api_key_header = "Authorization"
api_key_format = "Bearer {token}"
```

## Tool Permissions

Configure MCP tool permissions like built-in tools:

```toml
[tools.fetch_get]
permission = "always"

[tools.api_query]
permission = "ask"
```

## Related

- [MCP Overview](overview.md)
- [HTTP Transport](http-transport.md)
- [Stdio Transport](stdio-transport.md)
