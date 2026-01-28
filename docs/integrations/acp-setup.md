# ACP Setup

Kin Code can be used in text editors and IDEs that support [Agent Client Protocol](https://agentclientprotocol.com/overview/clients). This guide covers setup for various editors.

## Overview

The `kin-acp` command provides ACP server functionality. Once you have configured `kin` with API keys, you're ready to use `kin-acp` in your editor.

## Prerequisites

1. Install Kin Code: `uv tool install kin-code`
2. Configure API keys: `kin --setup`
3. Verify installation: `kin-acp --version`

## Editor Setup

### Zed

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

To use:
1. Open the "New Thread" pane (right sidebar)
2. Select "Kin Code" from the agent dropdown
3. Start the conversation

### JetBrains IDEs

Works with IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs.

Add to your `acp.json` (see [JetBrains documentation](https://www.jetbrains.com/help/ai-assistant/acp.html)):

```json
{
  "agent_servers": {
    "Kin Code": {
      "command": "kin-acp"
    }
  }
}
```

To use:
1. Open AI Chat (View > Tool Windows > AI Chat)
2. Select "Kin Code" from the agent selector
3. Start the conversation

### Neovim (avante.nvim)

Add to your Neovim configuration:

```lua
{
  acp_providers = {
    ["kin-code"] = {
      command = "kin-acp",
      env = {
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY"),
        -- Or your provider's API key
      },
    }
  }
}
```

## Configuration

### ACP-Specific Settings

The ACP server respects your Kin Code configuration. Settings in `~/.kin-code/config.toml` apply to ACP sessions.

### Environment Variables

Pass environment variables to the ACP server:

```json
{
  "agent_servers": {
    "Kin Code": {
      "command": "kin-acp",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "KIN_MODEL": "gpt-4o"
      }
    }
  }
}
```

### Working Directory

ACP sessions typically use the project root as the working directory. The editor handles this automatically.

## Troubleshooting

### Server Not Starting

1. Verify `kin-acp` is in your PATH:
   ```bash
   which kin-acp
   ```

2. Test the command directly:
   ```bash
   kin-acp --version
   ```

3. Check API keys are configured:
   ```bash
   kin --setup
   ```

### Authentication Errors

Ensure your API key is available to the ACP process:
- Set in `~/.kin-code/.env`
- Or pass via the `env` configuration

### Editor Not Showing Agent

1. Restart the editor
2. Check editor logs for errors
3. Verify the configuration syntax

## Features

When using Kin Code via ACP:

- Full access to all tools
- Project-aware context
- Same capabilities as CLI
- Session persistence (depends on editor)

## Limitations

ACP mode differs from CLI mode:

- No interactive approval prompts (tools auto-approve based on configuration)
- UI is provided by the editor
- Some slash commands may not be available

## Related

- [Zed Integration](zed.md)
- [JetBrains Integration](jetbrains.md)
- [Neovim Integration](neovim.md)
- [Configuration](../configuration/overview.md)
