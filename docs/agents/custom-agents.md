# Custom Agents

Create custom agent profiles for specific workflows.

## Creating an Agent

1. Create a TOML file in `~/.kin-code/agents/`:

```toml
# ~/.kin-code/agents/reviewer.toml

active_model = "gpt-4o"
system_prompt_id = "code-review"

disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

2. Use the agent:

```bash
kin --agent reviewer
```

## Configuration Options

### Model Selection

```toml
active_model = "gpt-4o"
```

### System Prompt

```toml
system_prompt_id = "my-prompt"
```

Create the prompt in `~/.kin-code/prompts/my-prompt.md`.

### Tool Configuration

```toml
# Disable tools
disabled_tools = ["bash"]

# Enable only specific tools
enabled_tools = ["read_file", "grep"]

# Per-tool permissions
[tools.read_file]
permission = "always"
```

### Agent Type

```toml
agent_type = "main"     # Default, for interactive use
agent_type = "subagent" # For task delegation
```

## Examples

### Read-Only Explorer

```toml
# explorer.toml
disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

### Trusted Automation

```toml
# automation.toml
[tools.bash]
permission = "always"

[tools.write_file]
permission = "always"
```

## Related

- [Agents Overview](overview.md)
- [Built-in Agents](built-in.md)
- [System Prompts](system-prompts.md)
