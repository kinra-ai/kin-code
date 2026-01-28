# Shell Tools

Tools for executing shell commands.

## bash

Execute shell commands.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | string | The command to execute |

### Examples

```
> bash(command="ls -la")
```

```
> bash(command="npm install")
```

```
> bash(command="git status")
```

### Features

- Full shell access
- Environment variable support
- Working directory context
- Output capture

### Notes

- Commands run in the project's working directory
- Environment inherits from Kin Code's environment
- Long-running commands may timeout
- Interactive commands are not supported

## Safety Considerations

The bash tool is powerful and potentially destructive. Consider:

1. **Review commands before approval** - Understand what will run
2. **Use restricted agents** - `plan` agent disables bash by default
3. **Configure permissions** - Set to `ask` for safety

## Permissions

Configure in `config.toml`:

```toml
[tools.bash]
permission = "ask"  # Recommended for safety
```

For automation:

```toml
[tools.bash]
permission = "always"  # Use with caution
```

## Best Practices

1. **Be specific in requests** - Clear instructions lead to safer commands
2. **Review output** - Check results before proceeding
3. **Use read-only commands first** - Verify before modifying

## Related

- [Tools Overview](overview.md)
- [Tool Permissions](permissions.md)
- [Agents Overview](../agents/overview.md)
