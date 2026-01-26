# read_file

Read file contents with support for large files through chunking.

## Overview

The `read_file` tool reads file contents safely, with built-in support for handling large files through offset and limit parameters.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the file (relative or absolute) |
| `offset` | integer | No | Line number to start reading from (0-indexed) |
| `limit` | integer | No | Maximum number of lines to read |

## Response

The response includes:
- `content`: The file content
- `was_truncated`: Boolean indicating if content was cut short

## Reading Large Files

For large files, use chunking:

```python
# Read first 1000 lines
read_file(path="large_file.txt", limit=1000)

# If was_truncated is true, read next chunk
read_file(path="large_file.txt", offset=1000, limit=1000)
```

## Examples

```python
# Read entire file (up to default limit)
read_file(path="src/main.py")

# Read first 50 lines
read_file(path="README.md", limit=50)

# Read lines 100-200
read_file(path="data.csv", offset=100, limit=100)
```

## Permissions

```toml
[tools.read_file]
permission = "ask"
allowlist = ["*.md", "*.txt"]  # Auto-approve for these patterns
```
