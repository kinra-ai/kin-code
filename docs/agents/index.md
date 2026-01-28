# Agents

Agents are configuration profiles that define how Kin Code behaves. This section covers built-in agents, creating custom agents, and using subagents for task delegation.

## Quick Links

| Topic | Description |
|-------|-------------|
| [Overview](overview.md) | Agent system introduction and concepts |
| [Built-in Agents](built-in.md) | default, plan, accept-edits, auto-approve |
| [Custom Agents](custom-agents.md) | Creating your own agent profiles |
| [Subagents](subagents.md) | Task delegation with background agents |
| [System Prompts](system-prompts.md) | Customizing agent instructions |

## What Are Agents?

An agent is a named configuration profile that controls:
- **Tool permissions** - Which tools are enabled and auto-approved
- **System prompts** - Instructions that guide the AI's behavior
- **Model selection** - Which AI model to use
- **Behavioral settings** - How the agent interacts with you

Different agents are suited for different tasks. Use a read-only agent for exploration, or an auto-approve agent for trusted bulk operations.

## Built-in Agents

Kin Code includes four built-in agents:

| Agent | Description | Best For |
|-------|-------------|----------|
| `default` | Balanced safety, asks for approval | General use |
| `plan` | Read-only, auto-approves safe tools | Code exploration |
| `accept-edits` | Auto-approves file edits | Refactoring sessions |
| `auto-approve` | Auto-approves everything | Trusted batch tasks |

### default

The standard agent for everyday use:

```bash
kin  # Uses default agent
```

- Requires approval for destructive operations
- Balanced between safety and productivity
- Suitable for most workflows

### plan

A read-only agent for exploration:

```bash
kin --agent plan
```

- Auto-approves `read_file` and `grep`
- Denies write operations
- Perfect for understanding unfamiliar code

### accept-edits

An agent that streamlines file editing:

```bash
kin --agent accept-edits
```

- Auto-approves `write_file` and `search_replace`
- Still asks for `bash` commands
- Ideal for refactoring sessions

### auto-approve

An agent that auto-approves everything:

```bash
kin --agent auto-approve
```

- All tools execute without asking
- Use with caution
- Best for trusted, repetitive tasks

## Selecting an Agent

### At Startup

```bash
kin --agent plan
```

### Mid-Session

```
> /agent accept-edits
```

### In Configuration

```toml
# config.toml
default_agent = "plan"
```

## How Agents Differ from Tools

| Concept | Description |
|---------|-------------|
| **Tools** | Capabilities the AI can use (read_file, bash, etc.) |
| **Agents** | Configurations that control tool permissions and behavior |

Think of tools as the building blocks, and agents as the blueprints that determine how those blocks are assembled.

## Agent Types

### Main Agents

Main agents are designed for interactive sessions with you:
- Respond to your prompts
- Ask for approvals when needed
- Run in the foreground

### Subagents

Subagents run in the background for delegated tasks:
- Invoked via the `task` tool
- Operate autonomously
- Return results to the main agent

Example:
```
> Research the best practices for async Python
Agent: I'll delegate this to a research subagent.
```

See [Subagents](subagents.md) for details.

## Creating Custom Agents

Create an agent by adding a TOML file to `~/.kin-code/agents/`:

```toml
# ~/.kin-code/agents/reviewer.toml

active_model = "gpt-4o"
system_prompt_id = "code-review"

# Read-only configuration
disabled_tools = ["write_file", "search_replace", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

Use your custom agent:

```bash
kin --agent reviewer
```

See [Custom Agents](custom-agents.md) for a complete guide.

## System Prompts

Agents use system prompts to guide the AI's behavior. You can:
- Use built-in prompts
- Create custom prompts
- Override prompts per-agent

Example custom prompt:

```toml
# ~/.kin-code/agents/security.toml

system_prompt_id = "security-review"
```

With a corresponding prompt file at `~/.kin-code/prompts/security-review.md`.

See [System Prompts](system-prompts.md) for details.

## Agent Configuration Reference

Full agent configuration options:

```toml
# Model selection
active_model = "gpt-4o"

# System prompt
system_prompt_id = "cli"

# Agent type
agent_type = "main"  # or "subagent"

# Tool configuration
disabled_tools = []
enabled_tools = []

[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"
```

## Best Practices

1. **Start with `default`** - Safe and flexible for most work
2. **Use `plan` for exploration** - Fast, safe code reading
3. **Use `accept-edits` for refactoring** - Streamlined file changes
4. **Create custom agents** - For specialized, repeatable workflows
5. **Be careful with `auto-approve`** - Only for trusted, well-understood tasks

## Agent vs. Auto-Approve Mode

| Concept | Description |
|---------|-------------|
| **Agent** | A complete configuration profile |
| **Auto-approve mode** | A toggle that overrides permissions temporarily |

You can combine them:

```bash
kin --agent plan  # Start with plan agent
# Press Shift+Tab to toggle auto-approve for the session
```

---

**Related Pages**

- [Tools](../tools/index.md) - Tool system and permissions
- [Configuration](../configuration/index.md) - Configuration file reference
- [Skills](../skills/index.md) - Extending functionality with skills
- [Documentation Home](../index.md) - All documentation sections
