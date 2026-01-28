# Session Management

Kin Code can save sessions and allow you to continue or resume them later. This is useful for long-running tasks or picking up where you left off.

## Session Logging

Sessions are logged when session logging is enabled in your configuration.

### Enabling Session Logging

In `~/.kin-code/config.toml`:

```toml
enable_session_logging = true
```

Sessions are saved to `~/.kin-code/logs/`.

## Continuing Sessions

### Continue Last Session

Use `--continue` or `-c` to continue from your most recent session:

```bash
kin --continue
```

```bash
kin -c
```

This restores:
- The full conversation history
- The current working directory
- Agent state and context

### Resume Specific Session

Use `--resume` with a session ID:

```bash
kin --resume abc123
```

Session IDs support partial matching:

```bash
kin --resume abc  # Matches abc123, abc456, etc.
```

## Finding Session IDs

Session IDs are displayed:
- When you start a new session
- In the session log filenames
- When running `--continue` (shows which session is being continued)

### Listing Sessions

View saved sessions in the logs directory:

```bash
ls ~/.kin-code/logs/
```

Session files are named with timestamps and IDs.

## Session Data

Sessions store:
- Conversation messages
- Tool call history
- Agent state
- Working directory
- Model and configuration

## Working Directory

By default, sessions restore to their original working directory.

### Changing Working Directory

Use `--workdir` to specify a different directory:

```bash
kin --continue --workdir /new/path
```

This continues the session but operates in the new directory.

## Session Lifecycle

```
New Session
    |
    v
[Active Session] <---> Compact (reduce context)
    |
    v
  Exit
    |
    v
[Saved Session]
    |
    +---> Continue (--continue)
    |
    +---> Resume (--resume ID)
```

## Tips

1. **Use continue for quick pickup** - `kin -c` is fast for recent work
2. **Use resume for specific sessions** - When you have multiple sessions
3. **Compact long sessions** - Use `/compact` to reduce context before saving
4. **Note session IDs** - For sessions you'll want to return to

## Troubleshooting

### "No session found"

- Ensure session logging is enabled
- Check that previous sessions completed (not crashed)
- Verify the logs directory exists

### "Session not compatible"

Sessions may become incompatible after:
- Major Kin Code updates
- Configuration changes
- Model changes

Start a new session if resumption fails.

### Session Too Large

If a session has grown too large:
1. Use `/compact` to summarize
2. Consider starting a new session
3. Reference the old session in your new prompt

## Configuration

### Session Logging Location

```toml
# In config.toml
log_directory = "~/.kin-code/logs"
```

### Disable Session Logging

```toml
enable_session_logging = false
```

Note: This prevents `--continue` and `--resume` from working.

## Related

- [Interactive Mode](interactive-mode.md)
- [Configuration Overview](../configuration/overview.md)
