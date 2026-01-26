# Custom Agents

Create specialized agent configurations for specific use cases.

## Overview

Custom agents allow you to define pre-configured profiles with specific models, prompts, and tool settings.

## Creating an Agent

Create a TOML file in `~/.kin-code/agents/`:

```bash
touch ~/.kin-code/agents/myagent.toml
```

## Agent Configuration

```toml
# ~/.kin-code/agents/myagent.toml

# Use a specific model
active_model = "devstral-2"

# Use a custom system prompt
system_prompt_id = "myagent"

# Disable certain tools
disabled_tools = ["bash"]

# Override tool permissions
[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

## Using an Agent

Run Kin with the `--agent` flag:

```bash
kin --agent myagent
```

Kin loads `~/.kin-code/agents/myagent.toml` and applies its configuration.

## Example: Read-Only Agent

```toml
# ~/.kin-code/agents/readonly.toml

# Only allow exploration tools
disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"

[tools.todo]
permission = "always"
```

## Example: Code Review Agent

```toml
# ~/.kin-code/agents/reviewer.toml

# Use a specialized prompt
system_prompt_id = "code_review"

# Read-only access
disabled_tools = ["write_file", "search_replace"]

[tools.bash]
permission = "ask"
allowlist = ["git diff *", "git log *"]
```

## Example: Red Team Agent

```toml
# ~/.kin-code/agents/redteam.toml

active_model = "devstral-2"
system_prompt_id = "redteam"

disabled_tools = ["search_replace", "write_file"]

[tools.bash]
permission = "always"

[tools.read_file]
permission = "always"
```

Note: This requires a corresponding prompt file at `~/.kin-code/prompts/redteam.md`.

## Available Options

Any `config.toml` option can be overridden in an agent config:

- `active_model` - Model to use
- `system_prompt_id` - System prompt
- `enabled_tools` / `disabled_tools` - Tool access
- `[tools.*]` - Per-tool permissions
- `mcp_servers` - MCP server configuration

## Tips

1. **Naming**: Agent names must be valid filenames (no spaces or special characters)
2. **Prompts**: Custom `system_prompt_id` requires a matching `.md` file in `~/.kin-code/prompts/`
3. **Inheritance**: Agent configs override global `config.toml` settings
4. **Combining**: Use `--agent` with other flags like `--plan` or `--auto-approve`
