# write_file

Create new files or overwrite existing ones.

## Overview

The `write_file` tool creates or overwrites files. By default, it prevents accidental overwrites.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the file (relative or absolute) |
| `content` | string | Yes | Content to write |
| `overwrite` | boolean | No | Must be `true` to overwrite existing files (default: `false`) |

## Safety Rules

- **New files**: Just provide `path` and `content`
- **Existing files**: Must set `overwrite: true` or the operation fails
- Parent directories are created automatically if they don't exist

## Best Practices

1. **Always read first** before overwriting to understand current contents
2. **Prefer `search_replace`** for editing existing files
3. **Only create new files** when explicitly required

## Examples

```python
# Create a new file
write_file(
    path="src/new_module.py",
    content="def hello():\n    return 'Hello World'"
)

# Overwrite existing file (read first!)
write_file(
    path="src/existing.py",
    content="# Updated content\ndef new_function():\n    pass",
    overwrite=True
)
```

## Permissions

```toml
[tools.write_file]
permission = "ask"
denylist = ["*.env", "*.key"]  # Never auto-approve sensitive files
```
