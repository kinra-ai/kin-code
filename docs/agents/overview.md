# Agents Overview

Agents are configuration profiles that define how Kin Code behaves. Different agents have different tool permissions, system prompts, and behaviors.

## What Is an Agent?

An agent is a named configuration that includes:
- Default tool permissions
- System prompt selection
- Model preferences
- Behavioral settings

## Built-in Agents

Kin Code includes several pre-configured agents:

### default

The standard agent for general use.
- Requires approval for all tool executions
- Balanced between safety and productivity
- Best for most use cases

```bash
kin  # Uses default agent
```

### plan

A read-only agent for exploration and planning.
- Auto-approves safe tools (`grep`, `read_file`)
- Denies write operations by default
- Useful for code exploration without changes

```bash
kin --agent plan
```

### accept-edits

An agent that auto-approves file edits.
- Auto-approves `write_file`, `search_replace`
- Still asks for `bash` commands
- Useful for code refactoring sessions

```bash
kin --agent accept-edits
```

### auto-approve

An agent that auto-approves everything.
- All tools execute without asking
- Use with caution
- Best for trusted, repetitive tasks

```bash
kin --agent auto-approve
```

## Selecting an Agent

### Command Line

```bash
kin --agent plan
```

### Mid-Session

```
> /agent accept-edits
```

## Agent Configuration

Agents are defined in TOML files in `~/.kin-code/agents/`:

```toml
# ~/.kin-code/agents/my-agent.toml

# Model selection
active_model = "gpt-4o"

# System prompt
system_prompt_id = "my-prompt"

# Agent type (main or subagent)
agent_type = "main"

# Tool configuration
disabled_tools = []

[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"
```

## Creating Custom Agents

1. Create a file in `~/.kin-code/agents/`:

```toml
# ~/.kin-code/agents/reviewer.toml

active_model = "gpt-4o"
system_prompt_id = "code-review"

# Read-only: disable all write tools
disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

2. Use your agent:

```bash
kin --agent reviewer
```

## Subagents

Subagents are agents designed for task delegation. They run in the background without user interaction.

### Creating a Subagent

```toml
# ~/.kin-code/agents/explore.toml

agent_type = "subagent"
active_model = "gpt-4o"

# Subagents typically have auto-approved tools
[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

### Using Subagents

The `task` tool delegates work to subagents:

```
> Can you explore the project structure?

Agent: I'll delegate this to the explore subagent.

> task(task="Analyze project structure", agent="explore")
```

## Agent Inheritance

Agent configuration inherits from defaults:
1. Built-in defaults
2. User `config.toml` settings
3. Agent-specific overrides

Only specified settings are overridden; others use defaults.

## Agent vs. Mode

- **Agent**: A complete configuration profile
- **Auto-approve mode**: A toggle that overrides permissions temporarily

You can combine them:

```bash
kin --agent plan  # Plan agent with its defaults
# Then press Shift+Tab to toggle auto-approve
```

## Best Practices

1. **Use `default` for general work** - Safe and flexible
2. **Use `plan` for exploration** - Fast, safe code reading
3. **Use `accept-edits` for refactoring** - Streamlined file changes
4. **Create custom agents** - For specialized workflows
5. **Be careful with `auto-approve`** - Only for trusted tasks

## Related

- [Built-in Agents](built-in.md)
- [Custom Agents](custom-agents.md)
- [Subagents](subagents.md)
- [System Prompts](system-prompts.md)
