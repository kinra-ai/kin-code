# MCP Servers

Extend Kin Code's capabilities with Model Context Protocol (MCP) servers.

## Overview

MCP (Model Context Protocol) allows external tools and services to be exposed to the agent. When you configure an MCP server, its tools become available alongside Kin's built-in tools.

## Configuration

Add MCP servers in `config.toml`:

```toml
[[mcp_servers]]
name = "my_server"
transport = "http"
url = "http://localhost:8000"
```

## Transport Types

### HTTP Transport

Standard HTTP connection to an MCP server:

```toml
[[mcp_servers]]
name = "my_http_server"
transport = "http"
url = "http://localhost:8000"
headers = { "Authorization" = "Bearer my_token" }
```

### Streamable HTTP

HTTP with streaming support:

```toml
[[mcp_servers]]
name = "my_streaming_server"
transport = "streamable-http"
url = "http://localhost:8001"
headers = { "X-API-Key" = "my_api_key" }
```

### Stdio Transport

For local MCP server processes:

```toml
[[mcp_servers]]
name = "fetch_server"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

## Configuration Fields

### Common Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Short alias for the server (used in tool names) |
| `transport` | Yes | Transport type: `http`, `streamable-http`, or `stdio` |
| `prompt` | No | Usage hint appended to tool descriptions |

### HTTP/Streamable-HTTP Fields

| Field | Description |
|-------|-------------|
| `url` | Base URL of the MCP server |
| `headers` | Additional HTTP headers |
| `api_key_env` | Environment variable containing API token |
| `api_key_header` | Header name for the token (default: `Authorization`) |
| `api_key_format` | Format string for header value (default: `Bearer {token}`) |

### Stdio Fields

| Field | Description |
|-------|-------------|
| `command` | Command to run |
| `args` | Command arguments |

## Authentication

### Using Headers Directly

```toml
[[mcp_servers]]
name = "my_server"
transport = "http"
url = "http://localhost:8000"
headers = { "Authorization" = "Bearer your_token_here" }
```

### Using Environment Variables

```toml
[[mcp_servers]]
name = "my_server"
transport = "http"
url = "http://localhost:8000"
api_key_env = "MY_SERVER_API_KEY"
api_key_header = "Authorization"
api_key_format = "Bearer {token}"
```

Set the environment variable:
```bash
export MY_SERVER_API_KEY="your_token_here"
```

## Tool Naming

MCP tools are named using the pattern `{server_name}_{tool_name}`.

For example, if server `fetch_server` provides a tool called `get`, it becomes `fetch_server_get`.

## Configuring MCP Tool Permissions

```toml
[tools.fetch_server_get]
permission = "always"

[tools.my_server_dangerous_action]
permission = "never"
```

## Example: Fetch Server

Install and configure the fetch MCP server:

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]

[tools.fetch_fetch]
permission = "ask"
```

The agent can now fetch web content using the `fetch_fetch` tool.

## Troubleshooting

### Server Not Connecting

1. Check the server is running and accessible
2. Verify the URL and port
3. Check authentication headers
4. Review Kin's logs for connection errors

### Tools Not Appearing

1. Ensure the server name follows naming rules (alphanumeric, underscores, hyphens)
2. Reload configuration with `/reload`
3. Restart Kin to re-initialize MCP connections
