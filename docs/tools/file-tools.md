# File Tools

Tools for reading and writing files.

## read_file

Read the contents of a file.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | string | Path to the file |

### Example

```
> read_file(path="src/main.py")
```

### Notes

- Returns file content as text
- Large files may be truncated
- Binary files are not supported

## write_file

Write content to a file.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | string | Path to the file |
| `content` | string | Content to write |

### Example

```
> write_file(path="output.txt", content="Hello, world!")
```

### Notes

- Creates the file if it doesn't exist
- Overwrites existing content
- Creates parent directories if needed

## search_replace

Find and replace text in a file.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | string | Path to the file |
| `old` | string | Text to find |
| `new` | string | Replacement text |

### Example

```
> search_replace(path="config.py", old="DEBUG = True", new="DEBUG = False")
```

### Notes

- Requires exact match of `old` text
- Only replaces first occurrence by default
- File must exist

## Permissions

Configure in `config.toml`:

```toml
[tools.read_file]
permission = "always"

[tools.write_file]
permission = "ask"

[tools.search_replace]
permission = "ask"
```

## Related

- [Tools Overview](overview.md)
- [Tool Permissions](permissions.md)
