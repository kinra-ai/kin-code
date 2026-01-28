# MCP Overview

Model Context Protocol (MCP) allows Kin Code to integrate with external tool servers.

## What Is MCP?

MCP is a protocol for connecting AI assistants to external tools and data sources. It provides a standard way to:

- Expose tools to AI agents
- Handle tool execution
- Manage authentication
- Stream responses

## Why Use MCP?

- **Extend capabilities** - Add tools without modifying Kin Code
- **Reuse servers** - Same MCP server works with multiple clients
- **Isolation** - Tools run in separate processes
- **Flexibility** - Choose from community servers or build your own

## MCP in Kin Code

### Adding an MCP Server

In `config.toml`:

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

### Using MCP Tools

MCP tools are named `{server_name}_{tool_name}`:

```
> fetch_get(url="https://example.com")
```

## Supported Transports

| Transport | Description |
|-----------|-------------|
| `stdio` | Local process via stdin/stdout |
| `http` | Remote HTTP server |
| `streamable-http` | HTTP with streaming support |

## Example Servers

### Fetch Server

Fetch web content:

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

### Custom Server

Your own MCP server:

```toml
[[mcp_servers]]
name = "custom"
transport = "http"
url = "http://localhost:8000"
```

## Related

- [MCP Configuration](configuration.md)
- [HTTP Transport](http-transport.md)
- [Stdio Transport](stdio-transport.md)
- [Tool Naming](tool-naming.md)
