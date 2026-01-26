# CLI Options

Complete reference for Kin Code command-line arguments.

## Usage

```bash
kin [OPTIONS] [PROMPT]
```

## Positional Arguments

| Argument | Description |
|----------|-------------|
| `PROMPT` | Initial prompt to start the session with |

## Options

### General

| Option | Description |
|--------|-------------|
| `-v`, `--version` | Show version and exit |
| `--setup` | Run API key setup and exit |
| `--add-provider` | Add an OpenAI-compatible provider interactively |

### Mode Selection

| Option | Description |
|--------|-------------|
| `--auto-approve` | Start in auto-approve mode (never ask for tool approval) |
| `--plan` | Start in plan mode (read-only tools for exploration) |

### Programmatic Mode

| Option | Description |
|--------|-------------|
| `-p`, `--prompt TEXT` | Run in programmatic mode: send prompt, auto-approve, output response, exit |
| `--output FORMAT` | Output format: `text` (default), `json`, or `streaming` |
| `--max-turns N` | Maximum number of agent turns (programmatic mode only) |
| `--max-price DOLLARS` | Maximum cost in dollars before stopping (programmatic mode only) |
| `--enabled-tools TOOL` | Enable specific tools (can be specified multiple times) |

### Session Management

| Option | Description |
|--------|-------------|
| `-c`, `--continue` | Continue from the most recent saved session |
| `--resume SESSION_ID` | Resume a specific session by ID (supports partial matching) |

### Agent Configuration

| Option | Description |
|--------|-------------|
| `--agent NAME` | Load agent configuration from `~/.kin-code/agents/NAME.toml` |

## Examples

### Basic Usage

```bash
# Start interactive mode
kin

# Start with a prompt
kin "Explain the project structure"

# Auto-approve all tools
kin --auto-approve

# Plan mode (read-only)
kin --plan
```

### Programmatic Mode

```bash
# Single prompt, text output
kin -p "List all Python files"

# JSON output for scripting
kin -p "Find security issues" --output json

# Streaming JSON
kin -p "Refactor main.py" --output streaming

# Limit execution
kin -p "Review code" --max-turns 10 --max-price 0.50

# Restrict tools
kin -p "Search for TODOs" --enabled-tools grep --enabled-tools read_file
```

### Session Management

```bash
# Continue last session
kin -c

# Resume specific session
kin --resume abc123
```

### Custom Agents

```bash
# Use a custom agent
kin --agent reviewer

# Agent with auto-approve
kin --agent writer --auto-approve
```

### Setup

```bash
# Configure API keys
kin --setup

# Add a new provider
kin --add-provider
```

## Tool Patterns

The `--enabled-tools` option supports:
- Exact names: `--enabled-tools bash`
- Glob patterns: `--enabled-tools "serena_*"`
- Regex with prefix: `--enabled-tools "re:^serena_.*$"`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (API error, configuration error, etc.) |
