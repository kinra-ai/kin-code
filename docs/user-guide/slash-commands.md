# Slash Commands

Slash commands are special commands that control Kin Code's behavior. They start with `/` and provide quick access to common actions.

## Using Slash Commands

Type `/` followed by the command name:

```
> /help
```

Autocompletion is available - type `/` and press `Tab` to see options.

## Built-in Commands

### Session Commands

#### /help

Display help information:

```
> /help
```

Shows available commands and basic usage.

#### /exit

Exit Kin Code:

```
> /exit
```

Equivalent to `Ctrl+D` or `Ctrl+C` twice.

#### /clear

Clear the conversation:

```
> /clear
```

Removes all messages from the current session.

#### /compact

Compact the session:

```
> /compact
```

Summarizes the conversation to reduce context usage. Useful for long sessions.

### Model Commands

#### /model

Change the active model:

```
> /model gpt-4o
> /model claude-3-5-sonnet
```

Lists available models if no argument given.

### Agent Commands

#### /agent

Switch agent profile:

```
> /agent plan
> /agent auto-approve
```

Changes the agent profile mid-session.

### Tool Commands

#### /tools

List available tools:

```
> /tools
```

Shows all enabled tools and their descriptions.

### Skill Commands

#### /skills

List active skills:

```
> /skills
```

Shows enabled skills and their slash commands.

## Custom Slash Commands

Skills can define custom slash commands. These appear alongside built-in commands.

### Creating Custom Commands

In your skill's `SKILL.md`:

```markdown
---
name: my-skill
user-invocable: true
---

# My Skill

When invoked with /my-skill, this skill will...
```

The skill becomes available as `/my-skill`.

### Viewing Custom Commands

All available commands (built-in and custom) appear in autocompletion when you type `/`.

## Command Syntax

### Arguments

Some commands accept arguments:

```
> /model gpt-4o
```

### No Arguments

Commands without arguments execute immediately:

```
> /clear
```

## Autocompletion

Type `/` and:
- See all available commands
- Start typing to filter
- Press `Tab` to complete
- Press `Enter` to execute

## Tips

1. **Use autocompletion** - Don't memorize all commands
2. **Check /help** - For quick reference
3. **Combine with shortcuts** - `/clear` + fresh start
4. **Create skill commands** - For repetitive workflows

## Related

- [Interactive Mode](interactive-mode.md)
- [Skills Overview](../skills/overview.md)
- [Keyboard Shortcuts](keyboard-shortcuts.md)
