# Config File Reference

Complete reference for the `config.toml` configuration file.

## File Location

- **User-level**: `~/.kin-code/config.toml`
- **Project-level**: `./.kin-code/config.toml`

Project configuration overrides user configuration.

## General Settings

### active_model

The default AI model to use.

```toml
active_model = "gpt-4o"
```

### system_prompt_id

The system prompt to use. Corresponds to a file in `~/.kin-code/prompts/`.

```toml
system_prompt_id = "cli"  # Uses prompts/cli.md
```

### enable_auto_update

Whether to automatically check for and install updates.

```toml
enable_auto_update = true  # default
```

### enable_session_logging

Whether to save sessions for later resumption.

```toml
enable_session_logging = true  # default
```

### log_directory

Where to store session logs.

```toml
log_directory = "~/.kin-code/logs"  # default
```

## Tool Settings

### enabled_tools

Whitelist of tools to enable. If set, only these tools are available.

```toml
enabled_tools = ["read_file", "grep", "bash"]
```

Supports patterns:
- Exact names: `"read_file"`
- Glob patterns: `"serena_*"`
- Regex: `"re:^mcp_.*$"`

### disabled_tools

Blacklist of tools to disable.

```toml
disabled_tools = ["bash", "write_file"]
```

Supports the same patterns as `enabled_tools`.

### [tools.TOOL_NAME]

Per-tool configuration.

```toml
[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"

[tools.write_file]
permission = "ask"
```

#### permission

Tool permission level:

| Value | Description |
|-------|-------------|
| `"always"` | Auto-approve, never ask |
| `"ask"` | Ask for each execution (default) |
| `"never"` | Always deny |

## MCP Server Configuration

### [[mcp_servers]]

Array of MCP server configurations.

```toml
[[mcp_servers]]
name = "my-server"
transport = "stdio"
command = "my-command"
args = ["arg1", "arg2"]
env = { "KEY" = "value" }
startup_timeout_sec = 10
tool_timeout_sec = 60
```

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Server identifier (used in tool names) |
| `transport` | string | `"stdio"`, `"http"`, or `"streamable-http"` |

#### Stdio Transport Fields

| Field | Type | Description |
|-------|------|-------------|
| `command` | string | Command to execute |
| `args` | array | Command arguments |
| `env` | table | Environment variables |

#### HTTP Transport Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Server URL |
| `headers` | table | HTTP headers |
| `api_key_env` | string | Env var containing API key |
| `api_key_header` | string | Header name for API key |
| `api_key_format` | string | Format string (e.g., `"Bearer {token}"`) |

#### Timeout Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `startup_timeout_sec` | number | 10 | Server startup timeout |
| `tool_timeout_sec` | number | 60 | Tool execution timeout |

## Skills Configuration

### skill_paths

Additional paths to search for skills.

```toml
skill_paths = [
  "/path/to/custom/skills",
  "~/my-skills"
]
```

### enabled_skills

Whitelist of skills to enable.

```toml
enabled_skills = ["code-review", "test-*"]
```

### disabled_skills

Blacklist of skills to disable.

```toml
disabled_skills = ["experimental-*"]
```

## Agent Configuration

Agent configuration files go in `~/.kin-code/agents/`:

```toml
# ~/.kin-code/agents/my-agent.toml

active_model = "gpt-4o"
system_prompt_id = "my-prompt"
disabled_tools = ["bash"]

[tools.read_file]
permission = "always"
```

Use with:

```bash
kin --agent my-agent
```

## Environment Variables

Some settings can be overridden via environment:

| Variable | Description |
|----------|-------------|
| `KIN_HOME` | Configuration directory |
| `KIN_MODEL` | Default model |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |

## Default Values

If not specified, these defaults apply:

```toml
active_model = ""  # Must be configured
system_prompt_id = "cli"
enable_auto_update = true
enable_session_logging = true
log_directory = "~/.kin-code/logs"
enabled_tools = []  # All enabled
disabled_tools = []  # None disabled
skill_paths = []
enabled_skills = []  # All enabled
disabled_skills = []  # None disabled
```

## Validation

Configuration is validated on startup. Common errors:

- Missing required fields
- Invalid model names
- Invalid permission values
- Malformed TOML syntax

## Example Configurations

### Minimal

```toml
active_model = "gpt-4o"
```

### Read-Only Mode

```toml
active_model = "gpt-4o"
disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

### Full Automation

```toml
active_model = "gpt-4o"

[tools.bash]
permission = "always"

[tools.read_file]
permission = "always"

[tools.write_file]
permission = "always"

[tools.search_replace]
permission = "always"
```

## Related

- [Overview](overview.md)
- [API Keys](api-keys.md)
- [Models](models.md)
- [Tool Permissions](../tools/permissions.md)
