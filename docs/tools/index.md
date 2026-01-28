# Tools

Tools are the capabilities that allow Kin Code to interact with your system. This section covers all built-in tools, how to configure them, and how to extend functionality with MCP servers.

## Quick Links

| Topic | Description |
|-------|-------------|
| [Overview](overview.md) | Introduction to the tool system |
| [File Tools](file-tools.md) | read_file, write_file, search_replace |
| [Search Tools](search-tools.md) | grep and code searching |
| [Shell Tools](shell-tools.md) | bash command execution |
| [Task Tools](task-tools.md) | todo and task delegation |
| [User Interaction](user-interaction.md) | ask_user_question |
| [Web Tools](web-tools.md) | Web browsing and fetching |
| [Permissions](permissions.md) | Configuring tool access |

## What Are Tools?

Tools are functions that Kin Code can call to perform actions on your behalf. When you ask the AI to do something, it uses tools to accomplish the task.

For example, when you ask "What's in the config file?", the agent uses the `read_file` tool to fetch the contents and then explains them to you.

## Tool Categories

### File Operations

Tools for reading, writing, and modifying files.

| Tool | Description | Permission Level |
|------|-------------|-----------------|
| `read_file` | Read file contents | Safe (read-only) |
| `write_file` | Create or overwrite files | Destructive |
| `search_replace` | Find and replace text | Destructive |

### Search

Tools for finding code and text.

| Tool | Description | Permission Level |
|------|-------------|-----------------|
| `grep` | Search files using patterns | Safe (read-only) |

### Shell

Tools for executing system commands.

| Tool | Description | Permission Level |
|------|-------------|-----------------|
| `bash` | Execute shell commands | Potentially destructive |

### Task Management

Tools for organizing work and delegation.

| Tool | Description | Permission Level |
|------|-------------|-----------------|
| `todo` | Manage a task list | Safe |
| `task` | Delegate work to subagents | Variable |

### User Interaction

Tools for communicating with you.

| Tool | Description | Permission Level |
|------|-------------|-----------------|
| `ask_user_question` | Ask clarifying questions | Safe |

### Web

Tools for internet access.

| Tool | Description | Permission Level |
|------|-------------|-----------------|
| `web_fetch` | Fetch content from URLs | Safe (read-only) |
| `web_search` | Search the web | Safe (read-only) |

## Tool Permission Levels

Each tool invocation can require different levels of approval:

| Permission | Behavior | Use Case |
|------------|----------|----------|
| `always` | Auto-approve, never ask | Safe tools like read_file |
| `ask` | Prompt for approval | Destructive tools like bash |
| `never` | Always deny | Disabled tools |

Configure permissions in `config.toml`:

```toml
[tools.read_file]
permission = "always"

[tools.bash]
permission = "ask"

[tools.write_file]
permission = "ask"
```

## Tool Execution Flow

When Kin Code uses a tool:

1. **Decision** - The AI decides a tool is needed
2. **Display** - You see the tool call and parameters
3. **Approval** - You approve or deny (if required)
4. **Execution** - The tool runs
5. **Result** - Output is shown and interpreted

## Enabling and Disabling Tools

### Disable Specific Tools

```toml
disabled_tools = ["bash", "write_file"]
```

### Enable Only Specific Tools

```toml
enabled_tools = ["read_file", "grep", "ask_user_question"]
```

### Pattern Matching

Use glob patterns or regex:

```toml
# Glob patterns
enabled_tools = ["read_*", "grep"]

# Regex patterns
enabled_tools = ["re:^(read|grep).*$"]
```

## MCP Tools

Extend Kin Code with external tools via [MCP (Model Context Protocol)](../mcp/overview.md):

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

MCP tools are named `{server_name}_{tool_name}`, for example `fetch_fetch`.

## Tool Safety

### Safe Tools (Read-Only)

These tools don't modify your system:
- `read_file` - Reads file contents
- `grep` - Searches for patterns
- `ask_user_question` - Asks you questions
- `web_fetch` - Fetches web content

Consider setting these to `permission = "always"` for faster workflows.

### Potentially Destructive Tools

These tools can modify your system:
- `write_file` - Creates or overwrites files
- `search_replace` - Modifies file contents
- `bash` - Executes arbitrary commands

Keep these at `permission = "ask"` unless you have a specific workflow that needs auto-approval.

## Tool Output Visibility

Toggle tool output visibility with `Ctrl+O` during a session. This helps you:
- See exactly what the agent is doing
- Debug unexpected behavior
- Verify operations before they complete

## Best Practices

1. **Start with defaults** - The default permission settings are safe
2. **Review before approving** - Read tool calls before pressing `y`
3. **Use agents** - Different agents have different tool permissions
4. **Configure for your workflow** - Auto-approve tools you trust

---

**Related Pages**

- [Configuration](../configuration/index.md) - Configure tool permissions
- [Agents](../agents/index.md) - Agents with different tool settings
- [MCP](../mcp/overview.md) - Add external tools
- [Documentation Home](../index.md) - All documentation sections
