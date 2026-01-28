# Zed Integration

Using Kin Code with the Zed editor.

## Prerequisites

1. Install Kin Code: `uv tool install kin-code`
2. Configure API keys: `kin --setup`
3. Install Zed editor

## Configuration

Add to `~/.config/zed/settings.json`:

```json
{
  "agent_servers": {
    "Kin Code": {
      "type": "custom",
      "command": "kin-acp",
      "args": [],
      "env": {}
    }
  }
}
```

## Usage

1. Open Zed
2. Open the "New Thread" pane (right sidebar)
3. Select "Kin Code" from the agent dropdown
4. Start chatting

## Custom Configuration

Pass environment variables:

```json
{
  "agent_servers": {
    "Kin Code": {
      "type": "custom",
      "command": "kin-acp",
      "args": [],
      "env": {
        "KIN_MODEL": "gpt-4o"
      }
    }
  }
}
```

## Troubleshooting

### Agent Not Appearing

1. Verify `kin-acp` is in PATH
2. Restart Zed
3. Check Zed logs

### Connection Issues

1. Test `kin-acp` directly in terminal
2. Verify API keys are configured
3. Check environment variables

## Related

- [ACP Setup](acp-setup.md)
- [Configuration](../configuration/overview.md)
