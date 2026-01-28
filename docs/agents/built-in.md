# Built-in Agents

Kin Code includes several pre-configured agent profiles.

## default

The standard agent for general use.

- **Tool permissions**: Ask for all tools
- **Use case**: General coding tasks

```bash
kin  # Uses default
```

## plan

Read-only agent for exploration.

- **Tool permissions**: Auto-approves `read_file`, `grep`
- **Disabled tools**: `write_file`, `search_replace`, `bash`
- **Use case**: Code exploration, planning

```bash
kin --agent plan
```

## accept-edits

Agent for file editing workflows.

- **Tool permissions**: Auto-approves `write_file`, `search_replace`
- **Use case**: Refactoring, code updates

```bash
kin --agent accept-edits
```

## auto-approve

Agent that auto-approves everything.

- **Tool permissions**: All tools auto-approved
- **Use case**: Trusted, repetitive tasks
- **Warning**: Use with caution

```bash
kin --agent auto-approve
```

## Comparing Agents

| Agent | read_file | write_file | bash | grep |
|-------|-----------|------------|------|------|
| default | ask | ask | ask | ask |
| plan | always | never | never | always |
| accept-edits | ask | always | ask | ask |
| auto-approve | always | always | always | always |

## Related

- [Agents Overview](overview.md)
- [Custom Agents](custom-agents.md)
