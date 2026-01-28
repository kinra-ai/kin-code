# Interactive Mode

Interactive mode is Kin Code's primary interface - a conversational chat where you interact with the AI agent in real-time.

## Starting Interactive Mode

Launch interactive mode by running `kin` without arguments:

```bash
kin
```

Or with an initial prompt:

```bash
kin "Explain this codebase"
```

## The Interface

### Header Bar

Shows current status:
- Model name and provider
- Working directory
- File count and git status

### Chat Area

Displays the conversation:
- Your messages
- Agent responses
- Tool calls and outputs

### Input Area

Where you type your messages:
- Supports multi-line input
- Autocompletion for files and commands
- History navigation

## Input Methods

### Single Line

Press `Enter` to send a single-line message.

### Multi-line

For multi-line input:
- Press `Ctrl+J` or `Shift+Enter` to add a new line
- Press `Enter` when done to send

### External Editor

Press `Ctrl+G` to open your message in an external editor. Useful for:
- Long, complex prompts
- Code snippets
- Formatted content

Set your preferred editor with `$EDITOR`:

```bash
export EDITOR=vim
```

## File References

Reference files in your prompt using `@`:

```
> Explain what @src/main.py does
```

Features:
- Tab completion for file paths
- Supports relative and absolute paths
- File content is included in context

## Shell Commands

Execute shell commands directly with `!`:

```
> !ls -la
> !git status
> !npm test
```

The command runs in your shell, bypassing the agent.

## Tool Approval

By default, the agent asks before executing tools:

```
Execute bash with command="npm test"? [y/n/always]
```

Options:
- `y` - Approve this execution
- `n` - Deny this execution
- `always` - Auto-approve this tool for the session

### Auto-Approve Mode

Toggle auto-approve with `Shift+Tab`:
- When enabled: All tools execute without asking
- When disabled: Each tool requires approval

The status bar shows the current mode.

## Views and Panels

### Tool Output View

Toggle with `Ctrl+O`:
- Shows detailed tool execution output
- Collapse to see just tool calls
- Expand to see full output

### Todo List View

Toggle with `Ctrl+T`:
- Shows the agent's task list
- Tracks progress on complex tasks
- Updated automatically as work progresses

## Navigation

### Message History

- `Up/Down` arrows to navigate previous messages
- `Ctrl+P/Ctrl+N` for previous/next

### Scrolling

- Mouse wheel to scroll
- `Page Up/Page Down` for larger jumps

## Interrupting

To interrupt the agent:
- Press `Ctrl+C` once to stop the current operation
- Press `Ctrl+C` twice to exit Kin Code

## Session Actions

### Clear Conversation

```
> /clear
```

Starts fresh while keeping the session.

### Compact Session

```
> /compact
```

Summarizes the conversation to save context space.

### Change Model

```
> /model gpt-4o
```

Switches to a different model mid-session.

## Exiting

To exit interactive mode:
- Type `/exit`
- Press `Ctrl+D`
- Press `Ctrl+C` twice

## Tips for Effective Use

1. **Be specific** - Clear requests get better results
2. **Use file references** - Help the agent find relevant code
3. **Review tool calls** - Understand what the agent is doing
4. **Use todo lists** - For complex multi-step tasks
5. **Compact when needed** - Keep context fresh for long sessions

## Related

- [Keyboard Shortcuts](keyboard-shortcuts.md)
- [Slash Commands](slash-commands.md)
- [File References](file-references.md)
- [Programmatic Mode](programmatic-mode.md)
