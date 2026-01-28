# CLI Reference

Complete reference for the `kin` command-line interface.

## Synopsis

```
kin [OPTIONS] [PROMPT]
```

## Description

Kin Code is an AI-powered CLI coding assistant. Run `kin` to start an interactive session, or provide a prompt for programmatic execution.

## Arguments

### PROMPT

Optional initial prompt. If provided, starts the session with this message.

```bash
kin "Explain this codebase"
```

## Options

### General Options

#### --help, -h

Show help message and exit.

```bash
kin --help
```

#### --version

Show version information.

```bash
kin --version
```

#### --setup

Run the setup wizard.

```bash
kin --setup
```

### Model Options

#### --model MODEL

Use a specific model for this session.

```bash
kin --model gpt-4o
kin --model claude-3-5-sonnet
```

### Agent Options

#### --agent AGENT

Use a specific agent profile.

```bash
kin --agent plan
kin --agent auto-approve
```

Built-in agents: `default`, `plan`, `accept-edits`, `auto-approve`

### Session Options

#### --continue, -c

Continue from the most recent session.

```bash
kin --continue
kin -c
```

#### --resume SESSION_ID

Resume a specific session by ID.

```bash
kin --resume abc123
```

Supports partial ID matching.

#### --workdir PATH

Set the working directory.

```bash
kin --workdir /path/to/project
```

### Programmatic Options

#### --prompt PROMPT

Run in programmatic mode with the given prompt.

```bash
kin --prompt "List all Python files"
```

#### --max-turns N

Limit the maximum number of agent turns.

```bash
kin --prompt "Analyze code" --max-turns 10
```

#### --max-price DOLLARS

Set a cost limit in dollars.

```bash
kin --prompt "Analyze code" --max-price 1.0
```

#### --enabled-tools TOOL

Enable specific tools (can be repeated).

```bash
kin --prompt "..." --enabled-tools read_file --enabled-tools grep
```

Supports:
- Exact names: `read_file`
- Glob patterns: `bash*`
- Regex: `re:^serena_.*$`

#### --output FORMAT

Set output format.

| Format | Description |
|--------|-------------|
| `text` | Human-readable (default) |
| `json` | All messages as JSON array |
| `streaming` | Newline-delimited JSON |

```bash
kin --prompt "..." --output json
```

### Approval Options

#### --auto-approve

Auto-approve all tool executions.

```bash
kin --auto-approve
```

Note: This is the default in programmatic mode.

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | API error |
| 4 | Interrupted (max-turns/max-price) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `KIN_HOME` | Configuration directory (default: `~/.kin-code`) |
| `KIN_MODEL` | Default model |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `EDITOR` | External editor for `Ctrl+G` |

## Examples

### Interactive Session

```bash
# Basic interactive mode
kin

# With initial prompt
kin "Explain the project structure"

# With specific model
kin --model gpt-4o "Review this code"

# With agent profile
kin --agent plan
```

### Programmatic Mode

```bash
# Basic programmatic
kin --prompt "List files"

# With limits
kin --prompt "Analyze code" --max-turns 5 --max-price 0.50

# With JSON output
kin --prompt "Summarize" --output json

# With restricted tools
kin --prompt "Read and analyze" --enabled-tools read_file --enabled-tools grep
```

### Session Management

```bash
# Continue last session
kin --continue

# Resume specific session
kin --resume abc123

# Different working directory
kin --workdir /other/project
```

## Configuration

Most options can be set in `~/.kin-code/config.toml`:

```toml
active_model = "gpt-4o"
enable_auto_update = true
```

Command-line options override configuration file settings.

## Related

- [Interactive Mode](../user-guide/interactive-mode.md)
- [Programmatic Mode](../user-guide/programmatic-mode.md)
- [Configuration](../configuration/overview.md)
