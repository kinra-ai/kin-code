# Programmatic Mode

Run Kin Code non-interactively for scripting and automation.

## Basic Usage

Use the `--prompt` or `-p` flag:

```bash
kin --prompt "Refactor the main function in cli/main.py to be more modular."
```

By default, programmatic mode uses auto-approve for all tool executions.

## Output Formats

Control the output format with the `--output` flag:

| Format | Description |
|--------|-------------|
| `text` | Human-readable output (default) |
| `json` | All messages as JSON at completion |
| `streaming` | Newline-delimited JSON per message |

Examples:

```bash
# Default text output
kin -p "List all Python files"

# JSON output for parsing
kin -p "List all Python files" --output json

# Streaming JSON for real-time processing
kin -p "List all Python files" --output streaming
```

## Limiting Execution

### Maximum Turns

Limit the number of agent turns (API round-trips):

```bash
kin -p "Fix the bug" --max-turns 5
```

### Maximum Cost

Set a cost limit in dollars:

```bash
kin -p "Refactor the codebase" --max-price 1.00
```

The session stops if the cost exceeds the limit.

## Enabling Specific Tools

In programmatic mode, you can restrict which tools are available:

```bash
# Only allow grep and read_file
kin -p "Search for TODO comments" --enabled-tools grep --enabled-tools read_file
```

This disables all other tools for the session.

## Piping Input

You can also pipe input to Kin:

```bash
echo "Explain this error" | kin -p
cat error.log | kin -p "What's causing this error?"
```

## Scripting Examples

### CI/CD Integration

```bash
#!/bin/bash
# Automated code review
kin -p "Review the code in src/ for security issues" \
    --output json \
    --max-turns 10 \
    --enabled-tools grep --enabled-tools read_file
```

### Batch Processing

```bash
#!/bin/bash
for file in src/*.py; do
    kin -p "Add docstrings to $file" --max-turns 3
done
```

## Next Steps

- Configure [Tool Permissions](../configuration/tool-permissions.md)
- Learn about [Session Management](./session-management.md)
