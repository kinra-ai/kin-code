# JetBrains Integration

Using Kin Code with JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.).

## Prerequisites

1. Install Kin Code: `uv tool install kin-code`
2. Configure API keys: `kin --setup`
3. JetBrains IDE with AI Assistant

## Configuration

Add to your `acp.json` ([JetBrains documentation](https://www.jetbrains.com/help/ai-assistant/acp.html)):

```json
{
  "agent_servers": {
    "Kin Code": {
      "command": "kin-acp"
    }
  }
}
```

## Usage

1. Open your JetBrains IDE
2. Open AI Chat (View > Tool Windows > AI Chat)
3. Select "Kin Code" from the agent selector
4. Start chatting

## Supported IDEs

- IntelliJ IDEA
- PyCharm
- WebStorm
- PhpStorm
- GoLand
- Rider
- CLion
- DataGrip
- And other JetBrains IDEs with AI Assistant

## Troubleshooting

### Agent Not Listed

1. Verify `acp.json` syntax
2. Restart the IDE
3. Check `kin-acp` is in PATH

### Connection Errors

1. Test `kin-acp --version` in terminal
2. Verify API keys
3. Check IDE logs

## Related

- [ACP Setup](acp-setup.md)
- [Configuration](../configuration/overview.md)
