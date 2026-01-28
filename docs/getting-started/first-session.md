# First Session

This guide walks you through your first Kin Code session in detail, explaining each part of the interface and workflow.

## Launching Kin Code

Start Kin Code from your project directory:

```bash
cd /path/to/your/project
kin
```

## The Interface

When Kin Code starts, you'll see:

```
Kin Code v0.x.x

Model: gpt-4o (OpenAI)
Working directory: /path/to/your/project
Files: 42 | Git: main (clean)

>
```

### Header Information

- **Model** - The active AI model and provider
- **Working directory** - Your current project path
- **Files** - Number of files in the project
- **Git** - Current branch and status (if in a git repository)

### The Prompt

The `>` character is your input prompt. Type your request here in natural language.

## Understanding the Workflow

### 1. You Make a Request

Type what you want to accomplish:

```
> Can you explain the structure of this project?
```

### 2. The Agent Thinks

Kin Code processes your request. You'll see the agent's reasoning:

```
The user wants to understand the project structure. I'll use the grep
and read_file tools to explore the codebase and identify key components.
```

### 3. Tools Are Executed

The agent uses tools to accomplish tasks:

```
> read_file(path="README.md")

[README.md content displayed]

> bash(command="find . -type f -name '*.py' | head -20")

[Python files listed]
```

### 4. You Approve or Deny

For each tool execution, you're asked to approve:

```
Execute read_file with path="README.md"? [y/n/always]
```

Your options:
- **y** - Approve this execution
- **n** - Deny (the agent will try a different approach)
- **always** - Auto-approve this tool for the session

### 5. The Agent Responds

After gathering information, the agent provides its response:

```
This is a Python web application with the following structure:

- `src/` - Main application code
  - `api/` - REST API endpoints
  - `models/` - Database models
  - `utils/` - Utility functions
- `tests/` - Test suite
- `config/` - Configuration files
...
```

## Tool Approval Modes

Kin Code has different modes for tool approval:

### Default Mode

Every tool execution requires explicit approval. This is the safest option.

### Auto-Approve Mode

Press `Shift+Tab` to toggle auto-approve mode. When enabled:
- All tools execute without asking
- Useful for trusted, repetitive tasks
- Toggle off when you want control back

### Agent-Specific Modes

Different agents have different default behaviors:
- **default** - Requires approval for all tools
- **plan** - Auto-approves read-only tools (grep, read_file)
- **accept-edits** - Auto-approves file edit tools
- **auto-approve** - Auto-approves everything

Select an agent with:

```bash
kin --agent plan
```

## Using File References

Reference files in your prompt using the `@` symbol:

```
> Explain what @src/main.py does
```

Kin Code provides autocompletion for file paths. Start typing after `@` to see suggestions.

## Using Slash Commands

Type `/` to see available commands:

```
> /help
```

Common commands:
- `/help` - Show help
- `/exit` - Exit Kin Code
- `/clear` - Clear the conversation
- `/model` - Change the model
- `/compact` - Compact the session to save context

## Keyboard Shortcuts

Essential shortcuts for your first session:

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Ctrl+J` | New line (multi-line input) |
| `Ctrl+C` | Interrupt current operation |
| `Ctrl+O` | Toggle tool output view |
| `Ctrl+T` | Toggle todo list view |
| `Shift+Tab` | Toggle auto-approve mode |
| `Ctrl+G` | Open external editor |
| `Tab` | Autocomplete |

## Understanding Tool Output

When tools execute, their output is displayed. You can toggle this view:

- Press `Ctrl+O` to show/hide tool output
- Collapsed view shows just the tool call
- Expanded view shows full output

## The Todo List

Kin Code maintains a todo list for complex tasks. Press `Ctrl+T` to view it:

```
TODO List:
[ ] Analyze project structure
[x] Read main configuration
[ ] Document API endpoints
```

The agent updates this list as work progresses.

## Ending Your Session

To end your session:

1. Type `/exit` or press `Ctrl+D`
2. Or use `Ctrl+C` twice

### Session Persistence

Sessions can be saved and resumed:

```bash
# Continue from last session
kin --continue

# Resume a specific session
kin --resume abc123
```

See [Session Management](../user-guide/session-management.md) for details.

## What's Next

Now that you understand the basics:

- [Interactive Mode](../user-guide/interactive-mode.md) - Deep dive into the interface
- [Slash Commands](../user-guide/slash-commands.md) - All available commands
- [Keyboard Shortcuts](../user-guide/keyboard-shortcuts.md) - Full shortcut reference
- [Configuration](../configuration/overview.md) - Customize your setup
