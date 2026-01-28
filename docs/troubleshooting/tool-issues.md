# Tool Issues

Solutions for tool execution problems.

## General Tool Issues

### "Tool not found"

Tool is not available.

**Solutions:**
1. Check tool name spelling
2. Verify tool isn't disabled in config
3. Check `enabled_tools` whitelist

### "Permission denied"

Tool execution was denied.

**Solutions:**
1. Approve when prompted
2. Check tool permission in config
3. Use a different agent profile

### "Tool execution failed"

Tool returned an error.

**Solutions:**
1. Check error message for details
2. Verify tool parameters are correct
3. Check file/resource exists

## File Tool Issues

### read_file Errors

**"File not found"**
- Check file path is correct
- Use absolute path if needed
- Verify file exists

**"Permission denied"**
- Check file permissions
- Run from appropriate directory

### write_file Errors

**"Directory not found"**
- Parent directory must exist
- Create directory first

**"Permission denied"**
- Check directory permissions
- Verify write access

### search_replace Errors

**"Text not found"**
- Exact match required
- Check for whitespace differences
- Read file first to verify content

## Shell Tool Issues

### bash Errors

**"Command not found"**
- Check command is installed
- Use full path to command
- Check PATH variable

**"Timeout"**
- Command took too long
- Use shorter-running alternative
- Check for infinite loops

**"Permission denied"**
- Check execute permissions
- Use sudo if appropriate

## MCP Tool Issues

### "MCP server not responding"

**Solutions:**
1. Check server is running
2. Verify connection settings
3. Check server logs
4. Restart the server

### "MCP tool timeout"

**Solutions:**
1. Increase `tool_timeout_sec`
2. Check server performance
3. Simplify the request

## Debugging

### Check Tool List

```
> /tools
```

### Check Configuration

```toml
# config.toml
disabled_tools = []
enabled_tools = []

[tools.tool_name]
permission = "ask"
```

### Verbose Output

Toggle tool output with `Ctrl+O` to see full responses.

## Related

- [Tools Overview](../tools/overview.md)
- [Tool Permissions](../tools/permissions.md)
- [Common Issues](common-issues.md)
