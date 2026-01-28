# HTTP Transport

Configure MCP servers using HTTP transport.

## Overview

HTTP transport connects to remote MCP servers over HTTP/HTTPS.

## Transport Types

### http

Standard HTTP transport:

```toml
[[mcp_servers]]
name = "api"
transport = "http"
url = "http://localhost:8000"
```

### streamable-http

HTTP with streaming support:

```toml
[[mcp_servers]]
name = "stream"
transport = "streamable-http"
url = "http://localhost:8001"
```

## Configuration

### Basic

```toml
[[mcp_servers]]
name = "server"
transport = "http"
url = "https://api.example.com"
```

### With Headers

```toml
[[mcp_servers]]
name = "server"
transport = "http"
url = "https://api.example.com"
headers = { "X-Custom-Header" = "value" }
```

### With Authentication

```toml
[[mcp_servers]]
name = "server"
transport = "http"
url = "https://api.example.com"
api_key_env = "API_KEY"
api_key_header = "Authorization"
api_key_format = "Bearer {token}"
```

The `{token}` placeholder is replaced with the value from `api_key_env`.

## Timeouts

```toml
[[mcp_servers]]
name = "server"
transport = "http"
url = "https://api.example.com"
startup_timeout_sec = 15
tool_timeout_sec = 120
```

## When to Use

- **Remote servers** - Servers running on other machines
- **Shared services** - Multiple clients using one server
- **Cloud deployments** - Servers running in the cloud

## Related

- [MCP Overview](overview.md)
- [MCP Configuration](configuration.md)
- [Stdio Transport](stdio-transport.md)
