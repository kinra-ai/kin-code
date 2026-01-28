# Search Tools

Tools for searching code and files.

## grep

Search files using patterns (regex supported).

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `pattern` | string | Search pattern (regex) |
| `path` | string | Path to search in |
| `include` | string | File pattern to include (optional) |
| `exclude` | string | File pattern to exclude (optional) |

### Examples

```
> grep(pattern="TODO", path=".")
```

```
> grep(pattern="def \\w+\\(", path="src/", include="*.py")
```

```
> grep(pattern="console.log", path=".", exclude="node_modules/*")
```

### Features

- Regex pattern support
- Recursive directory search
- File filtering with glob patterns
- Context lines around matches

### Notes

- Uses ripgrep (`rg`) when available for speed
- Falls back to Python regex search
- Large result sets may be truncated

## Permissions

Configure in `config.toml`:

```toml
[tools.grep]
permission = "always"  # Safe for read-only
```

## Tips

1. **Use specific paths** - Narrower searches are faster
2. **Use include patterns** - Filter to relevant file types
3. **Escape regex special characters** - Use `\\` for literal characters

## Related

- [Tools Overview](overview.md)
- [Tool Permissions](permissions.md)
