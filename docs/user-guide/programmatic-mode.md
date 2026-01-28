# Programmatic Mode

Programmatic mode allows you to run Kin Code non-interactively, useful for scripting, automation, and CI/CD pipelines.

## Basic Usage

Use the `--prompt` flag:

```bash
kin --prompt "List all Python files in the project"
```

Or pipe input:

```bash
echo "Analyze this codebase" | kin
```

## Default Behavior

In programmatic mode:
- Auto-approve is enabled by default
- Output is formatted for readability
- The session exits after completion

## Options

### Maximum Turns

Limit the number of agent turns:

```bash
kin --prompt "Refactor the code" --max-turns 10
```

The session stops after N agent turns, even if not complete.

### Maximum Price

Set a cost limit in dollars:

```bash
kin --prompt "Analyze the codebase" --max-price 1.0
```

The session is interrupted if costs exceed the limit.

### Enabled Tools

Restrict which tools are available:

```bash
kin --prompt "Read and analyze" --enabled-tools read_file --enabled-tools grep
```

Supports:
- Exact names: `read_file`
- Glob patterns: `bash*`
- Regex: `re:^serena_.*$`

### Output Format

Choose the output format:

```bash
# Human-readable text (default)
kin --prompt "..." --output text

# JSON array of all messages
kin --prompt "..." --output json

# Newline-delimited JSON per message
kin --prompt "..." --output streaming
```

## Output Formats

### Text (Default)

Human-readable output:

```
Agent: I'll list the Python files in the project.

> bash(command="find . -name '*.py'")

Found 42 Python files:
- src/main.py
- src/utils.py
...
```

### JSON

All messages as a JSON array:

```json
[
  {
    "role": "assistant",
    "content": "I'll list the Python files...",
    "tool_calls": [...]
  },
  {
    "role": "tool",
    "content": "src/main.py\nsrc/utils.py\n..."
  }
]
```

### Streaming

Newline-delimited JSON, one message per line:

```
{"role":"assistant","content":"I'll list..."}
{"role":"tool","content":"src/main.py\n..."}
{"role":"assistant","content":"Found 42 files..."}
```

Useful for real-time processing.

## Exit Codes

Kin Code returns meaningful exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | API error |
| 4 | Interrupted (max-turns/max-price) |

## Examples

### Code Analysis

```bash
kin --prompt "Analyze the code quality in src/" \
    --enabled-tools read_file --enabled-tools grep \
    --output json > analysis.json
```

### Automated Refactoring

```bash
kin --prompt "Rename 'oldFunction' to 'newFunction' in all files" \
    --max-turns 20 \
    --max-price 0.50
```

### CI/CD Integration

```bash
#!/bin/bash
kin --prompt "Run tests and report failures" \
    --max-turns 5 \
    --output text || exit 1
```

### Batch Processing

```bash
for file in src/*.py; do
  kin --prompt "Add type hints to @$file" --max-turns 3
done
```

## Environment Variables

Configure programmatic mode via environment:

```bash
export KIN_MODEL="gpt-4o"
export KIN_MAX_TURNS="10"
export KIN_AUTO_APPROVE="true"
```

## Working Directory

Specify a different working directory:

```bash
kin --prompt "Analyze the project" --workdir /path/to/project
```

## Combining with Shell

Capture output for further processing:

```bash
# Store result
result=$(kin --prompt "Summarize README.md" --output text)

# Process JSON output
kin --prompt "List files" --output json | jq '.[-1].content'
```

## Related

- [Interactive Mode](interactive-mode.md)
- [CLI Reference](../api-reference/cli-reference.md)
- [Output Formats](../api-reference/output-formats.md)
