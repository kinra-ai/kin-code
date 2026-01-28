# Task Tools

Tools for task management and delegation.

## todo

Manage a task list to track work.

### Operations

#### Add

```
> todo(operation="add", task="Implement error handling")
```

#### Complete

```
> todo(operation="complete", task_id=1)
```

#### List

```
> todo(operation="list")
```

### Features

- Track multi-step work
- Mark tasks complete
- Provides agent with memory of work progress

### Notes

- Todo list is visible in UI (toggle with `Ctrl+T`)
- Persists within session
- Helps agent stay organized on complex tasks

## task

Delegate work to a subagent.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `task` | string | Description of the task |
| `agent` | string | Subagent to use (optional) |

### Example

```
> task(task="Analyze the project structure", agent="explore")
```

### Features

- Runs work in parallel
- Uses separate context (doesn't overload main session)
- Subagent has its own tool permissions

### Built-in Subagents

- **explore** - Read-only codebase exploration

### Creating Custom Subagents

See [Subagents](../agents/subagents.md) for creating custom subagents.

## Permissions

```toml
[tools.todo]
permission = "always"  # Safe

[tools.task]
permission = "ask"  # Review delegations
```

## Related

- [Tools Overview](overview.md)
- [Subagents](../agents/subagents.md)
- [Tool Permissions](permissions.md)
