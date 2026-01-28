# Output Formats

Output format options for programmatic mode.

## Overview

Use `--output FORMAT` to control output:

```bash
kin --prompt "..." --output json
```

## Formats

### text (default)

Human-readable text output.

```bash
kin --prompt "List files" --output text
```

Output:

```
Agent: I'll list the files in the project.

> bash(command="ls")

src/
tests/
README.md

Found 3 items in the project root.
```

### json

All messages as a JSON array.

```bash
kin --prompt "List files" --output json
```

Output:

```json
[
  {
    "role": "assistant",
    "content": "I'll list the files..."
  },
  {
    "role": "tool",
    "name": "bash",
    "content": "src/\ntests/\nREADME.md"
  },
  {
    "role": "assistant",
    "content": "Found 3 items..."
  }
]
```

### streaming

Newline-delimited JSON, one message per line.

```bash
kin --prompt "List files" --output streaming
```

Output:

```
{"role":"assistant","content":"I'll list..."}
{"role":"tool","name":"bash","content":"src/\n..."}
{"role":"assistant","content":"Found 3 items..."}
```

## Use Cases

### text

- Human reading
- Simple scripts
- Debugging

### json

- Parsing complete results
- Integration with other tools
- Structured analysis

### streaming

- Real-time processing
- Long-running tasks
- Pipeline integration

## Processing Output

### JSON

```bash
kin --prompt "..." --output json | jq '.[-1].content'
```

### Streaming

```bash
kin --prompt "..." --output streaming | while read line; do
  echo "$line" | jq '.content'
done
```

## Related

- [CLI Reference](cli-reference.md)
- [Programmatic Mode](../user-guide/programmatic-mode.md)
