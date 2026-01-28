# File References

File references allow you to include file paths in your prompts using the `@` symbol. This helps the agent understand which files you're referring to.

## Basic Usage

Reference a file by typing `@` followed by the path:

```
> Explain what @src/main.py does
```

```
> Compare @src/old.py and @src/new.py
```

## Autocompletion

When you type `@`, autocompletion activates:

1. Type `@` to start
2. Begin typing the file path
3. Press `Tab` to see completions
4. Select a completion or continue typing
5. Press `Enter` or `Space` to confirm

## Path Formats

### Relative Paths

Paths relative to your working directory:

```
> @src/main.py
> @./config/settings.toml
> @../other-project/file.py
```

### Absolute Paths

Full system paths:

```
> @/Users/name/project/src/main.py
```

### Directory References

Reference directories to indicate scope:

```
> Analyze all files in @src/utils/
```

Note: Directory references help indicate intent but don't automatically include all files.

## Multiple References

Include multiple files in one prompt:

```
> Compare the implementations in @src/v1/handler.py and @src/v2/handler.py
```

## How It Works

When you use a file reference:

1. Kin Code recognizes the `@path` pattern
2. The path is validated and resolved
3. The agent sees the file path in your message
4. The agent can then read the file using tools

File references are hints to the agent - they indicate which files are relevant. The agent still uses tools like `read_file` to access the content.

## Examples

### Code Review

```
> Review @src/api/handlers.py for security issues
```

### Refactoring

```
> Refactor the function parse_config in @src/config.py
```

### Documentation

```
> Add docstrings to all functions in @src/utils.py
```

### Comparison

```
> What's the difference between @tests/test_old.py and @tests/test_new.py?
```

### Multiple Files

```
> These files should use the same pattern: @src/a.py @src/b.py @src/c.py
```

## Tips

1. **Use tab completion** - Faster and avoids typos
2. **Be specific** - Reference exact files rather than directories
3. **Combine with context** - Explain what you want done with the file
4. **Use for clarity** - Even if the agent could find the file, references make your intent clear

## Troubleshooting

### File Not Found in Completion

- Check you're in the correct directory
- Verify the file exists
- Try using a relative path from your current location

### Wrong File Referenced

- Check for similarly named files
- Use more specific paths
- Include parent directories in the path

## Related

- [Interactive Mode](interactive-mode.md)
- [Keyboard Shortcuts](keyboard-shortcuts.md)
