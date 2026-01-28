# Subagents

Subagents enable task delegation for parallel or specialized work.

## What Are Subagents?

Subagents are agents that run independently, handling delegated tasks without user interaction. They:

- Run in separate context (don't overload main session)
- Have their own tool permissions
- Return results to the main agent

## Using Subagents

The main agent uses the `task` tool:

```
> task(task="Analyze the project structure", agent="explore")
```

## Built-in Subagents

### explore

Read-only codebase exploration.

- Auto-approves `read_file`, `grep`
- Disables write tools
- Good for research and analysis

## Creating Custom Subagents

1. Create agent config with `agent_type = "subagent"`:

```toml
# ~/.kin-code/agents/analyzer.toml

agent_type = "subagent"
active_model = "gpt-4o"

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

2. Delegate to your subagent:

```
> task(task="Analyze code quality", agent="analyzer")
```

## Subagent Behavior

- **No user prompts** - Tools auto-approve based on config
- **Isolated context** - Separate conversation history
- **Results returned** - Output goes back to main agent

## Best Practices

1. **Limit tool access** - Subagents should have minimal permissions
2. **Clear task descriptions** - Help subagent understand the goal
3. **Use for specific tasks** - Not general conversation

## Related

- [Agents Overview](overview.md)
- [Task Tools](../tools/task-tools.md)
