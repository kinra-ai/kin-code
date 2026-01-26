# todo

Track tasks and progress during a session.

## Overview

The `todo` tool helps manage a simple task list for tracking progress on complex, multi-step work.

## Actions

| Action | Description |
|--------|-------------|
| `read` | View the current todo list |
| `write` | Replace the entire todo list |

## Todo Item Structure

Each item has:
- `id`: Unique identifier (string)
- `content`: Task description
- `status`: One of `pending`, `in_progress`, `completed`, `cancelled`
- `priority`: One of `high`, `medium`, `low`

## When to Use

**Use for:**
- Complex multi-step tasks (3+ distinct steps)
- Multiple tasks from user input
- Tracking progress on ongoing work
- Breaking down large features

**Skip for:**
- Single, straightforward tasks
- Trivial operations
- Purely informational requests

## Examples

```python
# Read current todos
todo(action="read")

# Create initial task list
todo(
    action="write",
    todos=[
        {"id": "1", "content": "Read existing code", "status": "pending", "priority": "high"},
        {"id": "2", "content": "Implement feature", "status": "pending", "priority": "high"},
        {"id": "3", "content": "Write tests", "status": "pending", "priority": "medium"},
    ]
)

# Mark task in progress
todo(
    action="write",
    todos=[
        {"id": "1", "content": "Read existing code", "status": "in_progress", "priority": "high"},
        {"id": "2", "content": "Implement feature", "status": "pending", "priority": "high"},
        {"id": "3", "content": "Write tests", "status": "pending", "priority": "medium"},
    ]
)
```

## Best Practices

1. **One task in progress**: Only mark one task `in_progress` at a time
2. **Update immediately**: Mark tasks complete right after finishing
3. **Full replacement**: When writing, include ALL todos you want to keep
4. **Keep it current**: Remove irrelevant tasks rather than marking cancelled

## Viewing Todos

Press `Ctrl+T` in interactive mode to toggle the todo list view.
