# ACP Setup

Kin Code can be used in text editors and IDEs that support [Agent Client Protocol](https://agentclientprotocol.com/overview/clients). Kin Code includes the `kin-acp` tool.
Once you have set up `kin` with the API keys, you are ready to use `kin-acp` in your editor. Below are the setup instructions for some editors that support ACP.

## Zed

Set up a local install as follows:

1. Go to `~/.config/zed/settings.json` and, under the `agent_servers` JSON object, add the following key-value pair to invoke the `kin-acp` command. Here is the snippet:

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

2. In the `New Thread` pane on the right, select the `kin` agent and start the conversation.

## JetBrains IDEs

1. Add the following snippet to your JetBrains IDE acp.json ([documentation](https://www.jetbrains.com/help/ai-assistant/acp.html)):

```json
{
  "agent_servers": {
    "Kin Code": {
      "command": "kin-acp",
    }
  }
}
```

2. In the AI Chat agent selector, select the new Kin Code agent and start the conversation.

## Neovim (using avante.nvim)

Add Kin Code in the acp_providers section of your configuration

```lua
{
  acp_providers = {
    ["kin-code"] = {
      command = "kin-acp",
      env = {
         OPENAI_API_KEY = os.getenv("OPENAI_API_KEY"), -- or your provider's API key env var
      },
    }
  }
}
```
