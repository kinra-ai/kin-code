# User Interaction Tools

Tools for interactive communication with the user.

## ask_user_question

Ask the user clarifying questions.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `questions` | array | List of questions to ask |

Each question has:

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | The question text |
| `options` | array | Answer options (optional) |

Each option has:

| Field | Type | Description |
|-------|------|-------------|
| `label` | string | Short option label |
| `description` | string | Longer description |

### Example

```
> ask_user_question(questions=[
    {
      "question": "What's the main goal?",
      "options": [
        {"label": "Performance", "description": "Make it run faster"},
        {"label": "Readability", "description": "Make it easier to understand"}
      ]
    }
  ])
```

### Features

- Multiple questions at once (displayed as tabs)
- 2-4 options per question
- Automatic "Other" option for free text
- Non-blocking for agent workflow

### Use Cases

- Clarifying ambiguous requests
- Choosing between approaches
- Gathering requirements
- Confirming before destructive actions

## Notes

- Questions display in the UI
- User can take time to respond
- Agent waits for response before continuing

## Permissions

```toml
[tools.ask_user_question]
permission = "always"  # Safe - just asks questions
```

## Related

- [Tools Overview](overview.md)
- [Interactive Mode](../user-guide/interactive-mode.md)
