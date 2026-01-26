# Interactive Mode

Interactive mode is the primary way to use Kin Code. It provides a rich terminal interface for conversational coding assistance.

## Starting Interactive Mode

Simply run `kin` to enter the interactive chat loop:

```bash
kin
```

Or start with an initial prompt:

```bash
kin "Explain the structure of this project"
```

## Multi-line Input

For complex prompts spanning multiple lines:

- Press `Ctrl+J` to insert a newline
- Press `Shift+Enter` (in supported terminals) for a newline
- Press `Enter` to submit your message

## File References

Reference files directly in your prompt using the `@` symbol:

```
> Read the file @src/agent.py and explain its main class
```

The `@` symbol triggers smart autocompletion for file paths in your project.

## Direct Shell Commands

Prefix any command with `!` to execute it directly in your shell, bypassing the agent:

```
> !ls -la
> !git status
> !npm test
```

This is useful for quick commands where you don't need the agent's involvement.

## Auto-Approve Toggle

While in interactive mode, press `Shift+Tab` to toggle auto-approve on/off. When enabled, all tool executions proceed without prompting.

## View Controls

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Toggle tool output view |
| `Ctrl+T` | Toggle todo list view |

## Interrupting the Agent

Press `Escape` to interrupt the agent while it's processing or to close dialogs.

## Next Steps

- Learn about [Programmatic Mode](./programmatic-mode.md) for scripting
- Explore [Keyboard Shortcuts](./keyboard-shortcuts.md)
- See all [Slash Commands](./slash-commands.md)
