# Quick Start

Get up and running with Kin Code in just a few minutes.

## Prerequisites

Before starting, ensure you have:

- Kin Code installed (see [Installation](installation.md))
- An API key from a supported provider

## Step 1: Navigate to Your Project

Open your terminal and navigate to the project you want to work on:

```bash
cd /path/to/your/project
```

## Step 2: Launch Kin Code

Start Kin Code by running:

```bash
kin
```

## Step 3: First-Time Setup

If this is your first time running Kin Code, it will:

1. Create a configuration directory at `~/.kin-code/`
2. Prompt you to select a provider and model
3. Ask for your API key if not already configured

Your API key is saved securely to `~/.kin-code/.env` for future sessions.

Alternatively, configure your API key in advance:

```bash
kin --setup
```

## Step 4: Start a Conversation

Once setup is complete, you'll see the Kin Code interface. Type your request in natural language:

```
> Can you find all TODO comments in this project?
```

Kin Code will use its tools to search your codebase and respond:

```
I'll search for TODO comments in the project.

> grep(pattern="TODO", path=".")

I found the following TODO comments in your project:
- src/main.py:42: TODO: Implement error handling
- src/utils.py:15: TODO: Add logging
...
```

## Step 5: Approve Tool Executions

By default, Kin Code asks for approval before executing tools. You'll see prompts like:

```
Execute grep with pattern="TODO"? [y/n/always]
```

- `y` - Approve this execution
- `n` - Deny this execution
- `always` - Auto-approve this tool for the session

Press `Shift+Tab` to toggle auto-approve mode for all tools.

## Example Interactions

### Exploring Code

```
> What does the main function in cli/main.py do?
```

### Making Changes

```
> Add error handling to the parse_config function
```

### Running Commands

```
> Run the test suite
```

### Refactoring

```
> Rename the variable 'x' to 'user_count' in analytics.py
```

## Quick Tips

| Action | How |
|--------|-----|
| Reference a file | Use `@` symbol: `@src/main.py` |
| Multi-line input | Press `Ctrl+J` or `Shift+Enter` |
| Run shell command directly | Prefix with `!`: `!ls -la` |
| Open external editor | Press `Ctrl+G` |
| View slash commands | Type `/` and see autocomplete |
| Toggle tool output | Press `Ctrl+O` |
| Toggle todo list | Press `Ctrl+T` |
| Exit | Type `/exit` or press `Ctrl+C` |

## Starting with a Prompt

You can start Kin Code with an initial prompt:

```bash
kin "Explain the project structure"
```

Or use the `--prompt` flag for programmatic mode:

```bash
kin --prompt "List all Python files"
```

## Next Steps

- [First Session](first-session.md) - Detailed walkthrough of the interface
- [Interactive Mode](../user-guide/interactive-mode.md) - Full interactive mode guide
- [Slash Commands](../user-guide/slash-commands.md) - Available commands
- [Configuration](../configuration/overview.md) - Customize your setup
