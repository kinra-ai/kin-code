# grep

Recursively search for patterns in files.

## Overview

The `grep` tool uses ripgrep under the hood to search for regular expression patterns across your codebase. It automatically ignores common non-code files (.pyc, .venv, etc.).

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | Yes | Regular expression pattern to search for |
| `path` | string | No | Directory or file to search (default: current directory) |

## Use Cases

- Find function definitions
- Locate variable usage
- Search for error messages
- Find TODO comments
- Trace imports

## Examples

```python
# Find all TODO comments
grep(pattern="TODO", path=".")

# Find function definitions
grep(pattern="def process_", path="src/")

# Find imports of a module
grep(pattern="from utils import", path=".")

# Search with regex
grep(pattern="class \w+Controller", path="src/")
```

## Performance

The `grep` tool is optimized for speed:
- Uses ripgrep's fast parallel search
- Respects .gitignore patterns
- Automatically skips binary files
- Ignores common non-code directories

## Permissions

```toml
[tools.grep]
permission = "always"  # Safe to auto-approve (read-only)
```
