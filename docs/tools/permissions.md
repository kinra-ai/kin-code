# Tool Permissions

Configure how tools require approval before execution.

## Permission Levels

| Level | Behavior |
|-------|----------|
| `always` | Auto-approve, never ask |
| `ask` | Ask for approval each time |
| `never` | Always deny |

## Configuration

In `config.toml`:

```toml
[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"

[tools.write_file]
permission = "ask"
```

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

Supports exact names, glob patterns, and regex:

```toml
# Glob patterns
disabled_tools = ["mcp_*"]

# Regex (prefix with re:)
enabled_tools = ["re:^(read|grep).*$"]
```

## Default Permissions

If not configured, tools default to:

| Tool | Default |
|------|---------|
| `read_file` | `ask` |
| `write_file` | `ask` |
| `search_replace` | `ask` |
| `bash` | `ask` |
| `grep` | `ask` |
| `todo` | `ask` |
| `task` | `ask` |
| `ask_user_question` | `always` |

## Agent-Specific Permissions

Agents can override permissions:

```toml
# ~/.kin-code/agents/readonly.toml
disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

## Runtime Approval

During a session:

```
Execute bash with command="npm test"? [y/n/always]
```

- `y` - Approve this execution
- `n` - Deny this execution
- `always` - Auto-approve this tool for the session

### Auto-Approve Mode

Press `Shift+Tab` to toggle auto-approve for all tools.

## Safety Recommendations

### Read-Only Tools

Safe to auto-approve:

```toml
[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

### Modifying Tools

Keep at `ask`:

```toml
[tools.write_file]
permission = "ask"

[tools.search_replace]
permission = "ask"

[tools.bash]
permission = "ask"
```

## Related

- [Tools Overview](overview.md)
- [Agents Overview](../agents/overview.md)
- [Configuration](../configuration/config-file.md)
