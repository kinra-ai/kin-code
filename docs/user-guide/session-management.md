# Session Management

Kin Code can save and resume conversation sessions.

## Continuing the Last Session

Resume your most recent session:

```bash
kin -c
# or
kin --continue
```

This loads the conversation history from your last session, preserving context.

## Resuming a Specific Session

Resume a session by its ID:

```bash
kin --resume SESSION_ID
```

Session IDs support partial matching - you don't need the full ID.

## Session Logs

Every session is logged to `~/.kin-code/logs/` (or your configured log directory).

### Finding Session Logs

Use the `/log` command during a session to see the current log file path:

```
> /log
Session log: ~/.kin-code/logs/session_20250126_143022.jsonl
```

### Log Format

Session logs are stored as JSONL (JSON Lines) files, with one JSON object per line containing:
- Messages (user and assistant)
- Tool calls and results
- Timestamps
- Token usage

## Configuring Session Logging

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
| `enabled` | Enable/disable session logging | `true` |
| `save_dir` | Directory for log files | `~/.kin-code/logs` |
| `session_prefix` | Prefix for log file names | `session` |

## Managing Session History

### Compacting History

When conversation context grows large, use `/compact` to summarize:

```
> /compact
```

This reduces token usage while preserving important context.

### Clearing History

Start fresh within a session:

```
> /clear
```

This clears all conversation history - the agent loses all previous context.

## Use Cases

| Scenario | Command |
|----------|---------|
| Continue where you left off | `kin -c` |
| Resume a specific task | `kin --resume abc123` |
| Start fresh | `kin` (no flags) |
| Debug session issues | Check `~/.kin-code/logs/` |
