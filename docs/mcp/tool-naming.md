# MCP Tool Naming

How MCP tools are named in Kin Code.

## Naming Convention

MCP tools are named:

```
{server_name}_{tool_name}
```

### Example

Server configuration:

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

If the server exposes a tool called `get`, it becomes:

```
fetch_get
```

## Using MCP Tools

Reference by full name:

```
> fetch_get(url="https://example.com")
```

## Tool Permissions

Configure using the full name:

```toml
[tools.fetch_get]
permission = "always"
```

## Pattern Matching

Use patterns to configure multiple MCP tools:

```toml
# All tools from a server
disabled_tools = ["fetch_*"]

# Regex pattern
enabled_tools = ["re:^fetch_.*$"]
```

## Listing MCP Tools

View available tools:

```
> /tools
```

MCP tools appear with their full names.

## Notes

- Server names should be short and descriptive
- Avoid special characters in server names
- Underscores separate server name from tool name

## Related

- [MCP Overview](overview.md)
- [MCP Configuration](configuration.md)
- [Tool Permissions](../tools/permissions.md)
