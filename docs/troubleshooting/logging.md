# Logging

Diagnose issues using session logs and debugging tools.

## Session Logs

Every interactive session is logged to `~/.kin-code/logs/`.

### Finding the Current Log

Use the `/log` command during a session:

```
> /log
Session log: /Users/you/.kin-code/logs/session_20250126_143022.jsonl
```

### Log File Format

Logs are stored as JSONL (JSON Lines) files. Each line is a JSON object containing:
- Message content (user/assistant)
- Tool calls and results
- Timestamps
- Token usage

### Viewing Logs

```bash
# View recent entries
tail -20 ~/.kin-code/logs/session_*.jsonl

# Pretty-print JSON
cat session_20250126.jsonl | jq .

# Search for errors
grep -i error ~/.kin-code/logs/session_*.jsonl
```

## Configuring Logging

In `config.toml`:

```toml
[session_logging]
enabled = true
save_dir = "~/.kin-code/logs"
session_prefix = "session"
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `enabled` | Enable/disable logging | `true` |
| `save_dir` | Log directory | `~/.kin-code/logs` |
| `session_prefix` | Log file prefix | `session` |

### Disabling Logging

```toml
[session_logging]
enabled = false
```

## Debugging Tips

### Check Configuration

View current configuration:

```bash
cat ~/.kin-code/config.toml
```

Validate TOML syntax:

```bash
python -c "import tomllib; tomllib.load(open('~/.kin-code/config.toml', 'rb'))"
```

### Test API Connection

Check your API key works:

```bash
curl -H "Authorization: Bearer $MISTRAL_API_KEY" \
     https://api.mistral.ai/v1/models
```

### Verbose Mode

For debugging MCP connections and other issues, check the log file for detailed information about:
- Server connections
- Tool discovery
- Error messages

### Environment Check

Verify environment:

```bash
# Check API key is set
echo $MISTRAL_API_KEY

# Check Kin is in PATH
which kin

# Check Python version
python --version
```

## Log Retention

Logs accumulate over time. To manage disk space:

```bash
# Remove logs older than 30 days
find ~/.kin-code/logs -name "*.jsonl" -mtime +30 -delete

# Check log directory size
du -sh ~/.kin-code/logs
```

## Reporting Issues

When reporting bugs, include:

1. **Error message**: Full text of any error
2. **Session log**: Relevant portions of the session log
3. **Configuration**: Your `config.toml` (remove API keys)
4. **Environment**: OS, Python version, Kin version (`kin --version`)
5. **Steps to reproduce**: What you were trying to do

Submit issues at: https://github.com/kinra-ai/kin-code/issues
