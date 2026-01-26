# Tool Permissions

Control when and how tools execute.

## Permission Levels

| Level | Behavior |
|-------|----------|
| `always` | Execute without asking |
| `ask` | Prompt for approval (default) |
| `never` | Never allow execution |

## Setting Permissions

In `config.toml`:

```toml
[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"

[tools.write_file]
permission = "ask"
```

## Allowlist and Denylist

Fine-tune permissions with patterns:

```toml
[tools.bash]
permission = "ask"
allowlist = ["git *", "ls *", "pwd"]  # Auto-approve these
denylist = ["rm -rf *", "sudo *"]     # Auto-deny these
```

Patterns support glob syntax.

## Enable/Disable Tools

### Disable Specific Tools

```toml
disabled_tools = ["bash", "write_file"]
```

### Enable Only Specific Tools

```toml
enabled_tools = ["grep", "read_file", "todo"]
```

When `enabled_tools` is set, all other tools are disabled.

### Pattern Matching

Both fields support:
- Exact names: `"bash"`
- Glob patterns: `"serena_*"`
- Regex with prefix: `"re:^serena_.*$"`

```toml
# Enable only MCP tools from serena server
enabled_tools = ["serena_*"]

# Disable all MCP tools
disabled_tools = ["mcp_*"]
```

## Runtime Approval

When prompted for tool approval:

| Key | Action | Persists |
|-----|--------|----------|
| `y` | Approve once | No |
| `n` | Deny once | No |
| `a` | Always approve this tool | Session |
| `v` | Never allow this tool | Session |

## Mode-Based Permissions

Different modes have different defaults:

| Mode | Tool Behavior |
|------|---------------|
| Default | All tools ask for approval |
| Plan | Only `grep`, `read_file`, `todo` available; auto-approved |
| Accept Edits | `write_file`, `search_replace` auto-approved |
| Auto Approve | All tools auto-approved |

## Per-Agent Permissions

Override permissions in agent configs:

```toml
# ~/.kin-code/agents/readonly.toml
disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

## MCP Tool Permissions

MCP tools follow the naming pattern `{server_name}_{tool_name}`:

```toml
[tools.fetch_server_get]
permission = "always"

[tools.my_server_dangerous_action]
permission = "never"
```
