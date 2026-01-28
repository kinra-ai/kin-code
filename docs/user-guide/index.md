# User Guide

This guide covers everything you need to know to use Kin Code effectively in your daily workflow. From basic interactions to advanced automation, you'll find detailed information on all features.

## Quick Links

| Topic | Description |
|-------|-------------|
| [Interactive Mode](interactive-mode.md) | The main chat interface for conversational AI |
| [Programmatic Mode](programmatic-mode.md) | Scripting and automation with command-line options |
| [Slash Commands](slash-commands.md) | Built-in commands like /help, /clear, /agent |
| [Keyboard Shortcuts](keyboard-shortcuts.md) | Essential shortcuts for efficient navigation |
| [File References](file-references.md) | Using @ syntax to reference files |
| [Session Management](session-management.md) | Continue, resume, and manage chat sessions |
| [Trust Folders](trust-folders.md) | Security controls for directory access |

## Core Features

### Interactive Mode

The primary way to use Kin Code is through interactive chat:

```bash
kin                      # Start a new session
kin "Explain this code"  # Start with a prompt
kin --continue           # Resume your last session
```

In interactive mode, you have a natural conversation with the AI about your codebase. The agent can read files, search code, execute commands, and make changes - all with your approval.

See [Interactive Mode](interactive-mode.md) for details.

### Programmatic Mode

For automation and scripting, use programmatic mode:

```bash
kin --prompt "Analyze security vulnerabilities" \
    --max-turns 5 \
    --output json
```

This mode is ideal for:
- CI/CD pipelines
- Batch processing
- Scripted workflows

See [Programmatic Mode](programmatic-mode.md) for details.

### File References

Reference files directly in your prompts using `@`:

```
> Explain what @src/main.py does
> Compare @old/config.py with @new/config.py
> Find similar patterns to @utils/helpers.py
```

The `@` syntax automatically reads file contents and includes them in your request.

See [File References](file-references.md) for details.

## Essential Shortcuts

Learn these shortcuts to work faster:

| Shortcut | Action |
|----------|--------|
| `Enter` | Send your message |
| `Ctrl+J` | Insert a new line |
| `Ctrl+C` | Cancel/interrupt operation |
| `Ctrl+O` | Toggle tool output visibility |
| `Shift+Tab` | Toggle auto-approve mode |
| `Up/Down` | Navigate message history |

See [Keyboard Shortcuts](keyboard-shortcuts.md) for the complete list.

## Slash Commands

Built-in commands provide quick access to features:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/clear` | Clear the conversation |
| `/compact` | Summarize conversation history |
| `/agent <name>` | Switch to a different agent |
| `/model <name>` | Switch to a different model |
| `/skills` | List available skills |

See [Slash Commands](slash-commands.md) for all commands.

## Common Workflows

### Code Exploration

```
> Give me an overview of this project structure
> What does the main function do?
> How does authentication work?
> Find all places where User.email is accessed
```

### Code Modification

```
> Add input validation to the signup function
> Refactor this class to use dependency injection
> Update the API response format to include timestamps
```

### Testing and Debugging

```
> Run the tests for the auth module
> This test is failing - help me debug it
> Add unit tests for the new validation logic
```

### Documentation

```
> Generate docstrings for the public functions in this file
> Explain this algorithm in the README
> What's missing from the API documentation?
```

## Security and Safety

### Tool Approval

By default, Kin Code asks for approval before executing potentially destructive operations:

- Writing or modifying files
- Executing shell commands
- Making network requests

You control what happens:
- Press `y` to approve
- Press `n` to deny
- Press `a` to auto-approve similar operations

### Trust Folders

Kin Code respects directory trust settings. Untrusted directories have limited tool access until you explicitly trust them.

See [Trust Folders](trust-folders.md) for security configuration.

### Auto-Approve Mode

Toggle auto-approve with `Shift+Tab` when you trust the current operations. Use with caution.

## Session Management

### Continuing Sessions

Resume your last session:

```bash
kin --continue
```

### Session History

Sessions are logged to `~/.kin-code/logs/` by default. You can:
- Review past sessions
- Continue from any previous session
- Disable logging in configuration

See [Session Management](session-management.md) for details.

## Tips for Effective Use

### Be Specific

Instead of:
```
> Fix the bug
```

Try:
```
> The login function raises an error when the email contains a + character. Fix the email validation.
```

### Provide Context

Instead of:
```
> Update the tests
```

Try:
```
> The User model now has an optional phone field. Update the user tests to cover this new field.
```

### Use File References

Instead of:
```
> Look at the config file and tell me what database is used
```

Try:
```
> What database does @config/database.py configure?
```

### Iterate

Complex changes work better as a conversation:

```
> First, let's understand the current authentication flow
> Now, let's add OAuth support to the login function
> Let's add tests for the new OAuth flow
```

---

**Related Pages**

- [Getting Started](../getting-started/index.md) - Installation and setup
- [Tools](../tools/index.md) - Available tools and permissions
- [Agents](../agents/index.md) - Agent profiles for different workflows
- [Configuration](../configuration/index.md) - Customization options
- [Documentation Home](../index.md) - All documentation sections
