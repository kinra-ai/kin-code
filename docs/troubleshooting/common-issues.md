# Common Issues

Solutions to frequently encountered problems.

## Installation Issues

### "Command not found: kin"

The `kin` command is not in your PATH.

**Solutions:**
1. Reinstall with `uv tool install kin-code`
2. Ensure `~/.local/bin` is in your PATH
3. Try running with full path

### "Python version not supported"

Kin Code requires Python 3.12+.

**Solutions:**
1. Install Python 3.12+
2. Use pyenv to manage versions
3. Specify Python version: `uv tool install kin-code --python 3.12`

## Configuration Issues

### "API key not found"

API key is not configured.

**Solutions:**
1. Run `kin --setup`
2. Set environment variable: `export OPENAI_API_KEY=...`
3. Add to `~/.kin-code/.env`

### "Configuration file invalid"

Syntax error in `config.toml`.

**Solutions:**
1. Check TOML syntax
2. Validate with a TOML linter
3. Remove and regenerate config

## Runtime Issues

### "Model not available"

The specified model isn't accessible.

**Solutions:**
1. Check model name spelling
2. Verify API key has access to the model
3. Try a different model

### "Rate limit exceeded"

Too many API requests.

**Solutions:**
1. Wait and retry
2. Use a different model
3. Check your API plan limits

### "Context length exceeded"

Conversation is too long.

**Solutions:**
1. Use `/compact` to summarize
2. Start a new session
3. Use `/clear` and re-explain

## Tool Issues

See [Tool Issues](tool-issues.md) for tool-specific problems.

## Terminal Issues

See [Terminal Issues](terminal-issues.md) for display problems.

## Getting Help

If your issue isn't listed:
1. Check the documentation
2. Search existing GitHub issues
3. Open a new issue with details

## Related

- [Terminal Issues](terminal-issues.md)
- [API Issues](api-issues.md)
- [Tool Issues](tool-issues.md)
