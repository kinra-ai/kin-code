# Common Issues

Solutions to frequently encountered problems.

## API Key Issues

### "Missing API key" Error

**Symptom**: Error message about missing environment variable.

**Solutions**:
1. Run `kin --setup` to configure interactively
2. Set the environment variable:
   ```bash
   export MISTRAL_API_KEY="your_key"
   ```
3. Add to `~/.kin-code/.env`:
   ```
   MISTRAL_API_KEY=your_key
   ```

### "Invalid API key" Error

**Symptom**: Authentication failures when connecting to the provider.

**Solutions**:
1. Verify your API key is correct
2. Check the key hasn't expired
3. Ensure the key has proper permissions
4. Re-run `kin --setup`

## Configuration Issues

### Config File Not Loading

**Symptom**: Changes to `config.toml` not taking effect.

**Solutions**:
1. Check file location: `~/.kin-code/config.toml` or `./.kin-code/config.toml`
2. Validate TOML syntax (use a TOML validator)
3. Use `/reload` to reload configuration
4. Restart Kin

### Custom Agent Not Found

**Symptom**: "Config not found" error with `--agent`.

**Solutions**:
1. Check file exists: `~/.kin-code/agents/NAME.toml`
2. Verify filename matches agent name exactly
3. Check TOML syntax

### Custom Prompt Not Found

**Symptom**: "Invalid system_prompt_id" error.

**Solutions**:
1. Check file exists: `~/.kin-code/prompts/NAME.md`
2. Verify `system_prompt_id` matches filename (without `.md`)
3. Ensure file is readable

## Tool Execution Issues

### Tool Permission Denied

**Symptom**: Tool execution blocked.

**Solutions**:
1. Check tool permissions in `config.toml`
2. Check if tool is in `disabled_tools`
3. Verify `enabled_tools` includes the tool (if set)
4. Press `a` to always allow, or adjust config

### Bash Commands Failing

**Symptom**: Shell commands return errors.

**Solutions**:
1. Test command directly in terminal
2. Check working directory
3. Ensure required programs are installed
4. Check PATH includes necessary directories

## Session Issues

### Cannot Resume Session

**Symptom**: Session not found with `-c` or `--resume`.

**Solutions**:
1. Check session logging is enabled
2. Verify log directory exists: `~/.kin-code/logs/`
3. Use full session ID or more characters for partial match
4. List sessions manually: `ls ~/.kin-code/logs/`

### Context Growing Too Large

**Symptom**: Slow responses, high token usage.

**Solutions**:
1. Use `/compact` to summarize history
2. Use `/clear` to start fresh
3. Lower `auto_compact_threshold` in config
4. Break tasks into smaller conversations

## Connection Issues

### API Timeout

**Symptom**: Requests timing out.

**Solutions**:
1. Check internet connectivity
2. Increase `api_timeout` in config
3. Try a different model
4. Check provider status page

### MCP Server Not Connecting

**Symptom**: MCP tools not available.

**Solutions**:
1. Verify server is running
2. Check URL and port
3. Test connection: `curl http://localhost:8000`
4. Review authentication headers
5. Check Kin logs for errors

## Display Issues

### Terminal Rendering Problems

**Symptom**: Garbled output, missing characters.

**Solutions**:
1. Try a different `textual_theme`
2. Ensure terminal supports Unicode
3. Update terminal emulator
4. Try in a different terminal

### Shift+Enter Not Working

**Symptom**: Can't insert newlines with Shift+Enter.

**Solutions**:
1. Run `/terminal-setup`
2. Use `Ctrl+J` as alternative
3. Configure terminal to send proper escape codes

## Performance Issues

### Slow Startup

**Symptom**: Kin takes a long time to start.

**Solutions**:
1. Reduce `max_files` in `project_context`
2. Lower `max_depth` for directory scanning
3. Reduce `timeout_seconds`
4. Check for slow MCP server connections

### High Memory Usage

**Symptom**: Kin consuming excessive memory.

**Solutions**:
1. Use `/compact` regularly
2. Lower `auto_compact_threshold`
3. Restart Kin periodically for long sessions
