# ACP Setup

Use Kin Code in text editors and IDEs via Agent Client Protocol (ACP).

## Overview

Kin Code includes `kin-acp`, a tool that exposes the agent to editors supporting [Agent Client Protocol](https://agentclientprotocol.com/overview/clients).

## Prerequisites

1. Kin Code installed and API keys configured
2. An editor that supports ACP

## Zed

### Using the Extension (Recommended)

Install the [Kin Code extension](https://zed.dev/extensions/kin-code) from Zed's extension marketplace.

### Manual Configuration

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

In the **New Thread** pane, select the `kin` agent to start.

## JetBrains IDEs

Add to your IDE's `acp.json` ([documentation](https://www.jetbrains.com/help/ai-assistant/acp.html)):

```json
{
  "agent_servers": {
    "Kin Code": {
      "command": "kin-acp"
    }
  }
}
```

Select Kin Code in the AI Chat agent selector.

## Neovim (avante.nvim)

Add Kin Code in the `acp_providers` section:

```lua
{
  acp_providers = {
    ["kin-code"] = {
      command = "kin-acp",
      env = {
         KIN_API_KEY = os.getenv("KIN_API_KEY"),
      },
    }
  }
}
```

## Environment Variables

When using `kin-acp` with editors, ensure your API keys are available as environment variables:

```bash
# In your shell profile (.bashrc, .zshrc, etc.)
export MISTRAL_API_KEY="your_key_here"
```

Or configure them in your editor's environment settings.

## Troubleshooting

### kin-acp Not Found

Ensure Kin Code is installed and the `kin-acp` command is in your PATH:

```bash
which kin-acp
```

If not found, reinstall Kin Code or add the installation directory to your PATH.

### Connection Issues

1. Test `kin-acp` directly in a terminal
2. Check API key is set correctly
3. Review editor logs for error messages
4. Ensure no firewall is blocking local connections
